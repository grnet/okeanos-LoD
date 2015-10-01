from rest_framework import viewsets
from rest_framework import status as rest_status
from rest_framework import mixins
from rest_framework.views import APIView
from .models import LambdaInstance, LambdaApplication, User
from .serializers import (UserSerializer, LambdaInstanceSerializer, LambdaApplicationSerializer)
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.parsers import JSONParser
from rest_framework.pagination import LimitOffsetPagination

from .authenticate_user import KamakiTokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .exceptions import CustomParseError, CustomNotFoundError, \
    CustomAlreadyDoneError

from .response_messages import ResponseMessages
import events

from django.conf import settings


def _paginate_response(request, default_response):
    """
    This method is used to paginate a list response. The pagination method used is the default
    Django Rest Framework pagination.
    :param request: The request given to the calling view.
    :return: Returns the paginated response.
    :rtype : object
    """

    # Check if pagination was requested.
    if 'limit' in request.query_params:

        # Check if limit parameter is a positive integer.
        limit = request.query_params.get('limit')
        try:
            limit = int(limit)

            # Check if limit parameter is not a negative integer.
            if limit >= 0:
                default_response = _alter_default_pagination_response(default_response)
            else:
                raise CustomParseError(CustomParseError.messages['limit_value_error'])
        except ValueError:
            raise CustomParseError(CustomParseError.messages['limit_value_error'])
    else:
        default_response.data = {"data": default_response.data}

    return default_response


def _alter_default_pagination_response(default_response):
    """
    This method is used to refactor the default response of the Django Rest Framework default
    pagination.
    :param default_response: The response that the default pagination returned.
    :return: The refactored response.
    :rtype : object
    """

    # Change the name or 'result' field to 'data'
    default_response.data['data'] = default_response.data['results']
    del default_response.data['results']

    # Add count, next and previous fields under pagination field.
    default_response.data['pagination'] = dict()
    default_response.data['pagination']['count'] = default_response.data['count']
    del default_response.data['count']
    default_response.data['pagination']['previous'] = default_response.data['previous']
    del default_response.data['previous']
    default_response.data['pagination']['next'] = default_response.data['next']
    del default_response.data['next']

    return default_response


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for viewing Users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LambdaUsersCounterView(APIView):
    """
    View for views active Lambda Users.
    """
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    def get(self, request, format=None):
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
            # This works only on Postgres
            lambdaUsersCount = LambdaInstance.objects.all(). \
                order_by('owner').distinct('owner').count()
        else:
            lambdaUsersCount = LambdaInstance.objects.values('owner').distinct().count()

        status_code = rest_status.HTTP_202_ACCEPTED
        return Response(
            {
                "status": {
                    "code": status_code,
                    "short_description": ResponseMessages.short_descriptions['lambda_users_count'],
                },
                "data": {
                    "count": str(lambdaUsersCount),
                }

            },
            status=status_code)


class LambdaInstanceView(mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    APIView for viewing lambda instances.
    """

    # The queryset is only the lambda applications the user making the response owns.
    def get_queryset(self):
        return LambdaInstance.objects.filter(owner=self.request.user)

    serializer_class = LambdaInstanceSerializer
    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer
    parser_classes = (JSONParser,)
    pagination_class = LimitOffsetPagination

    lookup_field = 'uuid'

    # POST /api/lambda_instances/
    def create(self, request, *args, **kwargs):
        """
        Create api call responder for lambda_instance. Assigns the creation task to a celery worker.
        :param request: The HTTP POST request making the call.
        :param args:
        :param kwargs:
        :return: A response object according to the outcome of the call.
        """
        data = request.data

        instance_name = data['name']
        uuid = data['uuid']
        instance_info = data['instance_info']
        owner = request.user
        status = data['status']
        failure_message = data['failure_message']

        matching_instances = LambdaInstance.objects.filter(uuid=uuid)
        if matching_instances.exists():
            raise CustomAlreadyDoneError(
                CustomAlreadyDoneError.messages['lambda_instance_already_exists']
            )

        # create the celery task
        create_event = events.createLambdaInstance.delay(uuid=uuid, instance_name=instance_name,
                                                         instance_info=instance_info, owner=owner,
                                                         status=status,
                                                         failure_message=failure_message)

        status_code = rest_status.HTTP_202_ACCEPTED
        if settings.DEBUG:
            return Response({"status":
                                 {
                                     "code": status_code,
                                     "short_description":
                                         ResponseMessages.short_descriptions['lambda_'
                                                                             'instances_'
                                                                             'create']
                                 },
                             "data": [{"id": uuid}],
                             "debug": create_event.status
                             }, status=status_code)
        else:
            return Response({"status": {"code": status_code,
                                        "short_description": ResponseMessages.short_descriptions[
                                            'lambda_instances_create']},
                             "data": [{"id": uuid}],
                             }, status=status_code)

    # POST /lambda_instances/[uuid]/status
    @detail_route(methods=['post'], url_path="status")
    def updateStatus(self, request, uuid, *args, **kwargs):
        """
        Update status of a lambda instance in the database API call responder. Assigns the update
        task to a celery worker.
        :param request: The request made by the user.
        :param uuid: The uuid of the Lambda Instance to alter.
        :param args:
        :param kwargs:
        :return: A response object according to the outcome of the call.
        """
        matching_instances = self.get_queryset().filter(uuid=uuid)
        if not matching_instances.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['lambda_instance_not_found'])

        data = request.data

        status = data['status']
        failure_message = data['failure_message'] if 'failure_message' in data else None

        matching_instance = LambdaInstanceSerializer(matching_instances[0]).data

        if status == matching_instance['status']:
            raise CustomAlreadyDoneError(CustomAlreadyDoneError
                                         .messages['lambda_instance_already']
                                         .format(state=status))

        update_event = events.updateLambdaInstanceStatus.delay(uuid, status, failure_message)

        status_code = rest_status.HTTP_202_ACCEPTED

        if settings.DEBUG:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                               'lambda_instances_update']},
                "data": [{"id": uuid}],
                "debug": update_event.status,
            }, status=status_code)
        else:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                               'lambda_instances_update']},
                "data": [{"id": uuid}],
            }, status=status_code)

    # DELETE /api/lambda_instances/[uuid]
    def destroy(self, request, uuid, *args, **kwargs):
        """
        Delete API call responder for Lambda Instances.
        Assigns the deletion task to a celery worker.
        :param request: The request made by the user.
        :param uuid: The uuid of the Lambda Instance to delete.
        :param args:
        :param kwargs:
        :return: A response object according to the outcome of the call.
        """
        lambda_instances = self.get_queryset().filter(uuid=uuid)
        if not lambda_instances.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['lambda_instance_not_found'])

        destroy_event = events.deleteLambdaInstance.delay(uuid)

        status_code = rest_status.HTTP_202_ACCEPTED

        if settings.DEBUG:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                               'lambda_instances_delete']},
                "data": [{"id": uuid}, ],
                "debug": destroy_event.status,
            }, status=status_code)
        else:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                               'lambda_instances_delete']},
                "data": [{"id": uuid}, ],
            }, status=status_code)

    # GET /api/lambda_instances
    def list(self, request, *args, **kwargs):
        """
        List API call responder for Lambda Instances. Lists all the lambda instances that
        the user making the call owns.
        :param request: The request made by the user.
        :param args:
        :param kwargs:
        :return: A response object according to the outcome of the call.
        """
        response = _paginate_response(request, super(LambdaInstanceView, self).list(request))
        return LambdaInstanceView._embed_status_to_response(response)

    @staticmethod
    def _embed_status_to_response(default_response):
        """
        Appends status information to the response object.
        :param default_response: the input response.
        :return: The updated with the status response.
        """
        default_response.data['status'] = dict()
        default_response.data['status']['code'] = default_response.status_code
        default_response.data['status']['short_description'] = \
            ResponseMessages.short_descriptions['lambda_instances_list']

        return default_response


class LambdaInstanceCounterView(APIView):
    """
    APIView class for showing the active lambda instances count.
    """
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    # GET /api/lambda_instances/count
    def get(self, request, format=None):
        activeLambdaInstances = LambdaInstance.objects.filter(status="20").count()
        status_code = rest_status.HTTP_200_OK
        return Response(
            {
                "status": {
                    "code": status_code,
                    "short_description":
                        ResponseMessages.short_descriptions['lambda_instances_count'],
                },
                "data": {
                    "count": str(activeLambdaInstances),
                }

            },
            status=status_code)


class LambdaApplicationView(mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """
    APIView for viewing lambda applications.
    """

    # The queryset is only the lambda applications the user making the response owns.
    def get_queryset(self):
        return LambdaApplication.objects.filter(owner=self.request.user)

    serializer_class = LambdaApplicationSerializer
    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer
    pagination_class = LimitOffsetPagination

    lookup_field = 'uuid'

    # POST /api/lambda_applications/
    def create(self, request, *args, **kwargs):
        """
        Create api call responder for lambda_application.
        Assigns the deletion task to a celery worker.
        :param request: The HTTP POST request making the call.
        :param args:
        :param kwargs:
        :return: A response object according to the outcome of the call.
        """
        data = request.data

        name = data['name']
        owner = request.user
        uuid = data['uuid']
        description = data['description']
        status = data['status']
        failure_message = data['failure_message']

        matching_applications = LambdaApplication.objects.filter(uuid=uuid)
        if matching_applications.exists():
            raise CustomAlreadyDoneError(
                CustomAlreadyDoneError.messages['lambda_application_already_exists']
            )

        create_event = events.createLambdaApplication.delay(
            uuid, status=status, name=name, description=description,
            owner=owner, failure_message=failure_message
        )

        status_code = rest_status.HTTP_202_ACCEPTED

        if settings.DEBUG:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                               'lambda_applications_create']},
                "debug": create_event.status,
                "data": [{"id": uuid}, ],
            }, status=status_code)
        else:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                               'lambda_application_create']},
                "data": [{"id": uuid}, ],
            }, status=status_code)

    # POST /api/lambda_applications/status
    @detail_route(methods=['post'], url_path="status")
    def updateStatus(self, request, uuid, *args, **kwargs):
        """
        Update status of a lambda application in the database API call responder. Assigns the update
        task to a celery worker.
        :param request: The request made by the user.
        :param uuid: The uuid of the Lambda Instance to alter.
        :param args:
        :param kwargs:
        :return: A response object according to the outcome of the call.
        """

        matching_applications = self.get_queryset().filter(uuid=uuid)
        if not matching_applications.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['application_not_found'])

        data = request.data
        status = data['status']
        failure_message = data['failure_message'] if 'failure_message' in data else None
        update_event = events.updateLambdaApplicationStatus.delay(uuid, status, failure_message)

        status_code = rest_status.HTTP_202_ACCEPTED

        matching_application = LambdaApplicationSerializer(matching_applications[0]).data
        if status == matching_application['status']:
            raise CustomAlreadyDoneError(CustomAlreadyDoneError
                                         .messages['lambda_instance_already']
                                         .format(state=status))

        if settings.DEBUG:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                               'lambda_applications_update']},
                "data": [{"id": uuid}],
                "debug": update_event.status,
            }, status=status_code)
        else:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                               'lambda_applications_update']},
                "data": [{"id": uuid}],
            }, status=status_code)

    def destroy(self, request, uuid, *args, **kwargs):
        """
        Delete API call responder for Lambda Applications.
        Assigns the deletion task to a celery worker.
        :param request: The request made by the user.
        :param uuid: The uuid of the Lambda Application to delete.
        :param args:
        :param kwargs:
        :return: A response object according to the outcome of the call.
        """
        applications = self.get_queryset().filter(uuid=uuid)
        if not applications.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['application_not_found'])

        destroy_event = events.deleteLambdaApplication.delay(uuid)

        status_code = rest_status.HTTP_202_ACCEPTED

        if settings.DEBUG:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                               'lambda_applications_delete']},
                "data": [{"id": uuid}, ],
                "debug": destroy_event.status,
            }, status=status_code)
        else:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                               'lambda_applications_delete']},
                "data": [{"id": uuid}, ],
            }, status=status_code)

    def list(self, request, *args, **kwargs):
        """
        List API call responder for Lambda Applications. Lists all the lambda applications that
        the user making the call owns.
        :param request: The request made by the user.
        :param args:
        :param kwargs:
        :return: A response object according to the outcome of the call.
        """
        response = _paginate_response(request, super(LambdaApplicationView, self).list(request))
        return LambdaApplicationView._embed_status_to_response(response)

    @staticmethod
    def _embed_status_to_response(default_response):
        # default_response.data = { "data": default_response.data }
        default_response.data['status'] = dict()
        default_response.data['status']['code'] = default_response.status_code
        default_response.data['status']['short_description'] = \
            ResponseMessages.short_descriptions['lambda_applications_list']

        return default_response


class LambdaApplicationCounterView(APIView):
    """
    APIView class for showing the active lambda applications count.
    """
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    def get(self, request, format=None):
        activeLambdaApplications = LambdaApplication.objects.filter(status="0").count()

        status_code = rest_status.HTTP_200_OK
        return Response(
            {
                "status": {
                    "code": status_code,
                    "short_description": ResponseMessages.short_descriptions[
                        'lambda_applications_count'
                    ],
                },
                "data": {
                    "count": str(activeLambdaApplications),
                }

            },
            status=status_code)
