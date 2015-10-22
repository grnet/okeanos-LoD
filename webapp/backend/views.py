import json
import uuid
import stat

from os import path, mkdir, chmod

from django.conf import settings
from django.core.urlresolvers import resolve

from rest_framework import viewsets, status, mixins
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.decorators import detail_route, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from rest_framework_xml.renderers import XMLRenderer

from fokia.utils import get_user_okeanos_projects, get_vm_parameter_values

from . import tasks, events
from .models import Application, LambdaInstance, LambdaInstanceApplicationConnection
from .exceptions import CustomParseError, CustomValidationError, CustomNotFoundError,\
    CustomAlreadyDoneError, CustomCantDoError
from .serializers import ApplicationSerializer, LambdaInstanceSerializer, LambdaInstanceInfo
from .authenticate_user import KamakiTokenAuthentication, get_public_key
from .response_messages import ResponseMessages


def _paginate_response(view, request, default_response):
    """
    This method is used to paginate a list response. The pagination method used is the default
    Django Rest Framework pagination.
    :param request: The request given to the calling view.
    :param view: The view object calling this method.
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
                default_response = _parse_default_pagination_response(default_response)
            else:
                raise CustomParseError(CustomParseError.messages['limit_value_error'])
        except ValueError:
            raise CustomParseError(CustomParseError.messages['limit_value_error'])
    else:
        # Add 'data' as the root element.
        default_response.data = {"data": default_response.data}

    # Add status field in response data.
    default_response.data['status'] = dict()
    default_response.data['status']['code'] = default_response.status_code

    # Remove any fields that the serializer adds but are not wanted on a list call.
    default_response.data = view.parse_list_response(default_response.data)

    return default_response


def _parse_default_pagination_response(default_response):
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


@api_view(['GET', 'OPTION'])
def authenticate(request):
    """
    Checks the validity of the authentication token of the user
    Use authenticate_user.KamakiTokenAuthentication
    """

    # request.META contains all the headers of the request
    auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]

    # If something is wrong with the given token, authenticate credentials will throw an exception
    # which will be correctly handled by the exception handler.
    authenticator = KamakiTokenAuthentication()
    authenticator.authenticate_credentials(auth_token)

    status_code = status.HTTP_200_OK
    return Response({"status": status_code,
                     "result": "Success"}, status=status_code)


class UserPublicKeysView(APIView):
    """
    Implements the API calls relevant to public keys on ~okeanos.
    """

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,

    # Retrieves all the saved public keys from a user's account on okeanos.
    def get(self, request, format=None):
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]

        public_keys = get_public_key(auth_token)

        return Response({"status": {
            "short_description": ResponseMessages.short_descriptions['user_public_keys'],
            "code": 200
        },
            "data": public_keys
        })


class UserOkeanosProjects(APIView):
    """
    Implements the API calls relevant with the user's ~okeanos projects.
    """

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,

    # Retrieves all the ~okeanos projects on which the user is a member.
    def get(self, request, format=None):
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        okeanos_projects = get_user_okeanos_projects(auth_url, auth_token)

        status_code = status.HTTP_200_OK
        return Response({
            'status': {
                'short_description': ResponseMessages.short_descriptions['user_okeanos_projects'],
                'code': status_code
            },
            'data': okeanos_projects
        }, status=status_code)


class VMParameterValues(APIView):
    """
    Implements the API calls relevant to the values of the parameters for creating a VM on
    ~okeanos
    """

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,

    # Retrieves all the allowed values of the parameters for creating a VM
    def get(self, request, format=None):
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        vm_parameter_values = get_vm_parameter_values(auth_url, auth_token)

        status_code = status.HTTP_200_OK
        return Response({
            'status': {
                'short_description': ResponseMessages.short_descriptions['vm_parameter_values'],
                'code': status_code
            },
            'data': [vm_parameter_values]
        }, status=status_code)


class ApplicationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Implements the API calls relevant to applications.
    """

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,

    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    lookup_field = 'uuid'

    # The Pithos container on which user's applications are saved.
    pithos_container = "lambda_applications"

    def get_queryset(self):
        """
        Overrides the default get_queryset method.
        """

        # If the requested url directs to list-deployed view, then, change the query set to
        # the applications deployed on the specified lambda instance.
        if resolve(self.request.path_info).view_name == "application-list-deployed":
            lambda_instance_uuid = self.kwargs['uuid']

            # Check if the specified lambda instance exists.
            lambda_instances = LambdaInstance.objects.filter(uuid=lambda_instance_uuid)
            if not lambda_instances.exists():
                raise CustomNotFoundError(CustomNotFoundError.messages['lambda_instance_not_found'])
            lambda_instance = lambda_instances[0]

            # Get the applications that are deployed on the specified lambda instance.
            connections = LambdaInstanceApplicationConnection.objects.\
                filter(lambda_instance=lambda_instance)
            applications = [connection.application for connection in connections]

            return applications
        else:
            return Application.objects.all()

    def list(self, request, format=None):
        """
        This method is used to get a list of all the uploaded applications. Responds to GET
        requests on url r'^{prefix}{trailing_slash}$'
        """

        # Get the default Django Rest Framework pagination response.
        default_response = super(ApplicationViewSet, self).list(request)

        return _paginate_response(self, request, default_response)

    def create(self, request, format=None):
        """
        This method is used to upload an application to Pithos. Responds to POST requests on url
        r'^{prefix}{trailing_slash}$'
        """

        # Check if a file was sent with the request.
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            raise CustomParseError(CustomParseError.messages['no_file_error'])

        # Check if another file with same name already exists.
        if self.get_queryset().filter(name=uploaded_file.name).count() > 0:
            raise CustomParseError(CustomParseError
                                        .messages['filename_already_exists_error'])

        # Get the description provided with the request.
        description = request.data.get('description', '')

        # Get the type of the uploaded application
        app_type = request.data.get('type', '').lower()
        if app_type != 'batch' and app_type != 'streaming':
            raise CustomParseError(CustomParseError.messages['no_type_error'])

        # Get the name of the project provided.
        project_name = request.data.get('project_name', '')

        # Generate a uuid for the uploaded application.
        application_uuid = uuid.uuid4()

        # Create an event to insert a new entry on the database.
        events.create_new_application.delay(application_uuid, uploaded_file.name,
                                            self.pithos_container, description,
                                            app_type, request.user)

        # Save the uploaded file on the local file system.
        if not path.exists(settings.TEMPORARY_FILE_STORAGE):
            mkdir(settings.TEMPORARY_FILE_STORAGE)
            chmod(settings.TEMPORARY_FILE_STORAGE, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        local_file_path = path.join(settings.TEMPORARY_FILE_STORAGE, uploaded_file.name)
        local_file = open(local_file_path, 'wb+')

        # Django suggest to always save the uploaded file using chunks. That will avoiding reading
        # the whole file into memory and possibly overwhelming it.
        for chunk in uploaded_file.chunks():
            local_file.write(chunk)
        local_file.close()

        # Create a task to upload the application from the local file system to Pithos.
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        tasks.upload_application_to_pithos.delay(auth_url, auth_token, self.pithos_container,
                                                 project_name, local_file_path, application_uuid)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({"status": {"code": status_code, "short_description":
                                                         ResponseMessages.short_descriptions[
                                                             'application_upload']
                                    },
                         "data": [{
                             "id": application_uuid,
                             "links": {
                                 "self": request.build_absolute_uri() +
                                 "{id}".format(id=application_uuid)
                             }
                         }]}, status=status_code)

    def retrieve(self, request, uuid, format=None):
        """
        This method is used to get information about a specified application. Responds to GET
        requests on url r'^{prefix}/{lookup}{trailing_slash}$'
        """

        # Check if the specified application exists.
        applications = Application.objects.filter(uuid=uuid)
        if not applications.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['application_not_found'])
        serializer = ApplicationSerializer(applications[0])
        data = serializer.data

        # Rename uuid to id.
        data['id'] = data['uuid']
        del data['uuid']

        # Create status field.
        message = Application.status_choices[int(data['status'])][1]
        data['status'] = {'message': message,
                          'code': data['status'],
                           'detail': ResponseMessages.application_status_details[message]}

        # Change the type to a human readable format.
        data['type'] = Application.type_choices[int(data['type'])][1]

        # Show failure message only if it is not empty.
        if 'failure_message' in data:
            if data['failure_message'] == "":
                del data['failure_message']
            else:
                data['status']['failure_message'] = data['failure_message']
                del data['failure_message']

        # Return an appropriate response.
        status_code = status.HTTP_200_OK
        response = dict({"status":
                             {"code": status_code,
                              "short_description": ResponseMessages.
                                   short_descriptions['application_details']
                              },
                         "data": None
                         })

        response['data'] = [data]
        return Response(response, status=status_code)

    def destroy(self, request, uuid, format=None):
        """
        This method is used to delete an application from Pithos. Responds to DELETE requests on
        url r'^{prefix}/{lookup}{trailing_slash}$'
        """

        # Check if the specified application exists.
        applications = self.get_queryset().filter(uuid=uuid)
        if not applications.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['application_not_found'])
        serializer = ApplicationSerializer(applications[0])

        # Create task to delete the specified application from Pithos.
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        tasks.delete_application_from_pithos.delay(auth_url, auth_token, self.pithos_container,
                                                   serializer.data['name'], uuid)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({
            "status": {
                'code': status_code,
                'short_description': ResponseMessages.short_descriptions['application_delete']
            }}, status=status_code)

    @detail_route(methods=['post'])
    def deploy(self, request, uuid, format=None):
        """
        This method is used to deploy an application to a specified lambda instance. Responds to
        POST requests on url r'^{prefix}/{lookup}/{methodname}{trailing_slash}$'
        """

        application_uuid = uuid

        # Check if the lambda instance id was provided with the request.
        lambda_instance_uuid = request.data.get('lambda_instance_id')
        if not lambda_instance_uuid:
            raise CustomParseError(CustomParseError.messages['no_lambda_instance_id_error'])

        # Check if the specified lambda instance exists.
        lambda_instances = LambdaInstance.objects.filter(uuid=lambda_instance_uuid)
        if not lambda_instances.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['lambda_instance_not_found'])
        lambda_instance = lambda_instances[0]

        # Check if the specified application exists.
        applications = self.get_queryset().filter(uuid=application_uuid)
        if not applications.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['application_not_found'])
        application = applications[0]

        # Check the status of the specified lambda instance.
        if lambda_instance.status != LambdaInstance.STARTED:
            raise CustomCantDoError(CustomCantDoError.messages['cant_do'].
                                    format(action="deploy", object="an application",
                                           status=LambdaInstance.status_choices[
                                               int(lambda_instance.status)][1]))

        # Check if the specified application is already deployed on the specified lambda instance.
        if LambdaInstanceApplicationConnection.objects.filter(lambda_instance=lambda_instance,
                                                              application=application).exists():
            raise CustomAlreadyDoneError(CustomAlreadyDoneError.
                                         messages['application_already_deployed'])

        # Create a task to deploy the application.
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        tasks.deploy_application.delay(auth_url, auth_token, self.pithos_container,
                                       lambda_instance_uuid, application_uuid)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({
            "status": {
                'code': status_code,
                'short_description': ResponseMessages.short_descriptions['application_deploy']
            }}, status=status_code)

    @detail_route(methods=['get'], url_path="list-deployed")
    def list_deployed(self, request, uuid, format=None):
        """
        This method is used to list the deployed applications on a specified lambda instance.
        Responds to GET requests on url r'^{prefix}/{lookup}/{methodname}{trailing_slash}$
        """

        lambda_instance_uuid = uuid

        # Check if the specified lambda instance exists.
        lambda_instance = LambdaInstance.objects.filter(uuid=lambda_instance_uuid)
        if not lambda_instance.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['lambda_instance_not_found'])

        # Get the default Django Rest Framework pagination response.
        default_response = super(ApplicationViewSet, self).list(request)

        return _paginate_response(self, request, default_response)

    @detail_route(methods=['post'])
    def withdraw(self, request, uuid, format=None):
        """
        This method is used to withdraw an application from a specified lambda instance. Responds
        to POST requests on url r'^{prefix}/{lookup}/{methodname}{trailing_slash}$'
        """

        application_uuid = uuid

        # Check if the lambda instance id was provided with the request.
        lambda_instance_uuid = request.data.get('lambda_instance_id')
        if not lambda_instance_uuid:
            raise CustomParseError(CustomParseError.messages['no_lambda_instance_id_error'])

        # Check if the specified lambda instance exists.
        lambda_instances = LambdaInstance.objects.filter(uuid=lambda_instance_uuid)
        if not lambda_instances.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['lambda_instance_not_found'])
        lambda_instance = lambda_instances[0]

        # Check if the specified application exists.
        applications = self.get_queryset().filter(uuid=application_uuid)
        if not applications.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['application_not_found'])
        application = applications[0]

        # Check the status of the specified lambda instance.
        if lambda_instance.status != LambdaInstance.STARTED:
            raise CustomCantDoError(CustomCantDoError.messages['cant_do'].
                                    format(action="withdraw", object="an application",
                                           status=LambdaInstance.status_choices[
                                               int(lambda_instance.status)][1]))

        # Check if the specified application is already not deployed on the specified lambda
        # instance.
        if not LambdaInstanceApplicationConnection.objects.\
                filter(lambda_instance=lambda_instance, application=application).exists():
            raise CustomAlreadyDoneError(CustomAlreadyDoneError.
                                         messages['application_not_deployed'])

        # Create a task to withdraw the application.
        tasks.withdraw_application.delay(lambda_instance_uuid, application_uuid)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({
            "status": {
                'code': status_code,
                'short_description': ResponseMessages.short_descriptions['application_withdraw']
            }}, status=status_code)

    @detail_route(methods=['post'])
    def start(self, request, uuid, format=None):
        """
        This method is used to start an application on a specified lambda instance. Responds
        to POST requests on url r'^{prefix}/{lookup}/{methodname}{trailing_slash}$'
        """

        application, lambda_instance, instanceapplication = \
            self.get_application_instance_connection(request, uuid)

        if instanceapplication.started:
            raise CustomAlreadyDoneError(CustomAlreadyDoneError.
                                         messages['application_already_started'])

        if application.type == application.BATCH:
            app_type = 'batch'
            if lambda_instance.started_batch:
                raise CustomAlreadyDoneError(CustomAlreadyDoneError.
                                             messages['job_already_started']
                                             .format(type=app_type))
        else:
            app_type = 'streaming'
            if lambda_instance.started_streaming:
                raise CustomAlreadyDoneError(CustomAlreadyDoneError.
                                             messages['job_already_started']
                                             .format(type=app_type))

        lambda_instance_uuid = lambda_instance.uuid
        app_action = 'start'
        filename = application.name

        # Create a task to start the application.
        tasks.start_stop_application.delay(lambda_instance_uuid=lambda_instance_uuid,
                                           app_uuid=uuid, app_action=app_action,
                                           app_type=app_type, jar_filename=filename)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({
            "status": {
                'code': status_code,
                'short_description': ResponseMessages.short_descriptions['application_start']
            }}, status=status_code)

    @detail_route(methods=['post'])
    def stop(self, request, uuid, format=None):
        """
        This method is used to stop an application on a specified lambda instance. Responds
        to POST requests on url r'^{prefix}/{lookup}/{methodname}{trailing_slash}$'
        """

        application, lambda_instance, instanceapplication = \
            self.get_application_instance_connection(request, uuid)

        if not instanceapplication.started:
            raise CustomAlreadyDoneError(CustomAlreadyDoneError.
                                         messages['application_already_stopped'])

        if application.type == application.BATCH:
            app_type = 'batch'
            if not lambda_instance.started_batch:
                raise CustomAlreadyDoneError(CustomAlreadyDoneError.
                                             messages['job_already_stopped']
                                             .format(type=app_type))
        else:
            app_type = 'streaming'
            if not lambda_instance.started_streaming:
                raise CustomAlreadyDoneError(CustomAlreadyDoneError.
                                             messages['job_already_stopped']
                                             .format(type=app_type))

        lambda_instance_uuid = lambda_instance.uuid
        app_action = 'stop'

        # Create a task to stop the application.
        tasks.start_stop_application.delay(lambda_instance_uuid=lambda_instance_uuid,
                                           app_uuid=uuid, app_action=app_action, app_type=app_type)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({
            "status": {
                'code': status_code,
                'short_description': ResponseMessages.short_descriptions['application_stop']
            }}, status=status_code)

    def get_application_instance_connection(self, request, uuid):
        """
        Return the application and lambda instance connection object. The lambda instance uuid
        is contained into the request, while the application uuid is given as an argument.
        """

        application_uuid = uuid

        # Check if the lambda instance id was provided with the request.
        lambda_instance_uuid = request.data.get('lambda_instance_id')
        if not lambda_instance_uuid:
            raise CustomParseError(CustomParseError.messages['no_lambda_instance_id_error'])

        # Check if the specified lambda instance exists.
        lambda_instances = LambdaInstance.objects.filter(uuid=lambda_instance_uuid)
        if not lambda_instances.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['lambda_instance_not_found'])
        lambda_instance = lambda_instances[0]

        # Check if the specified application exists.
        applications = self.get_queryset().filter(uuid=application_uuid)
        if not applications.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['application_not_found'])
        application = applications[0]

        # Check the status of the specified lambda instance.
        if lambda_instance.status != LambdaInstance.STARTED:
            raise CustomCantDoError(CustomCantDoError.messages['cant_do'].
                                    format(action="start/stop", object="an application",
                                           status=LambdaInstance.status_choices[
                                               int(lambda_instance.status)][1]))

        # Check if the specified application is deployed on the specified lambda instance
        instanceapplications = LambdaInstanceApplicationConnection.objects.\
            filter(lambda_instance=lambda_instance, application=application)
        if not instanceapplications.exists():
            raise CustomNotFoundError(CustomNotFoundError.
                                      messages['application_not_deployed_on_instance'])
        instanceapplication = instanceapplications[0]

        return application, lambda_instance, instanceapplication

    def parse_list_response(self, response):
        """
        This method is used to remove from a list response any fields that the serializer adds
        but are not wanted in a list response
        """

        wanted_fields = ['uuid', 'name', 'status', 'failure_message', 'type']
        unwanted_fields = set(ApplicationSerializer.Meta.fields) - set(wanted_fields)

        for application in response['data']:
            for unwanted_field in unwanted_fields:
                del application[unwanted_field]

        response['status']['short_description'] = ResponseMessages.short_descriptions[
            'applications_list']

        for application in response['data']:
            application['status'] = {
                'code': application['status'],
                'message': Application.status_choices[int(application['status'])][1],
                'detail': ResponseMessages.application_status_details[
                    Application.status_choices[int(application['status'])][1]]
            }
            if application['failure_message'] != "":
                application['status']['failure_message'] = application['failure_message']
            del application['failure_message']

            application['type'] = Application.type_choices[int(application['type'])][1]

        # Change uuid name to id
        for item in response['data']:
            if 'uuid' in item:
                item['id'] = item['uuid']
                del item['uuid']

        return response


class LambdaInstanceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Implements the API calls relevant to interacting with lambda instances.
    """

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,

    queryset = LambdaInstance.objects.all().exclude(status='6')
    serializer_class = LambdaInstanceSerializer

    lookup_field = 'uuid'

    def list(self, request, format=None):
        """
        This method is used to get a list of all lambda instances. Responds to GET
        requests on url r'^{prefix}{trailing_slash}$'
        """

        # Get the default Django Rest Framework pagination response.
        default_response = super(LambdaInstanceViewSet, self).list(request)

        return _paginate_response(self, request, default_response)

    def retrieve(self, request, uuid, format=None):
        """
        This method is used to get information about a specified lambda instance. Responds to GET
        requests on url r'^{prefix}/{lookup}{trailing_slash}$'
        """

        # Check if the specified lambda instance exists.
        lambda_instances = LambdaInstance.objects.filter(uuid=uuid)
        if not lambda_instances.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['lambda_instance_not_found'])
        serializer = LambdaInstanceSerializer(lambda_instances[0])

        filter = request.query_params.get('filter', '')

        if filter == "status":
            wanted_fields = ['uuid', 'name', 'status', 'failure_message']
        elif filter == "info":
            wanted_fields = ['uuid', 'name', 'instance_info', 'master_node']
        elif filter == "":
            wanted_fields = ['uuid', 'name', 'instance_info', 'status', 'failure_message',
                             'applications', 'master_node']
        else:
            raise CustomParseError(CustomParseError.messages['filter_value_error'])

        unwanted_fields = set(LambdaInstanceSerializer.Meta.fields) - set(wanted_fields)

        lambda_instance_all = serializer.data
        # Remove unwanted fields from lambda instance information.
        for unwanted_field in unwanted_fields:
            del lambda_instance_all[unwanted_field]

        # Parse instance info field.
        if 'instance_info' in lambda_instance_all:
            lambda_instance_all['instance_info'] = json.loads(
                lambda_instance_all['instance_info'])
            lambda_instance_all['instance_info']['master_node_id'] = lambda_instance_all[
                'master_node']

        # If status exists, create a code field and change status to a human readable format.
        if 'status' in lambda_instance_all:
            lambda_instance_all['code'] = lambda_instance_all['status']
            lambda_instance_all['status'] = LambdaInstance.status_choices[
                int(lambda_instance_all['status'])][1]
            lambda_instance_all['details'] = ResponseMessages.lambda_instance_status_details[
                lambda_instance_all['status']]

        # Return an appropriate response.
        status_code = status.HTTP_200_OK
        response = {"status": {"code": status_code,
                               "short_description": ResponseMessages.
                                   short_descriptions['lambda_instance_details']
                               },
                    "data": None
                    }
        if filter == "status":
            data = [{
                "status": {
                    "code": lambda_instance_all['code'],
                    "message": lambda_instance_all['status'],
                    "detail": lambda_instance_all['details']
                },
                "id": lambda_instance_all['uuid'],
                "name": lambda_instance_all['name']
            }]

            # Add failure message only if it is not empty.
            if 'failure_message' in lambda_instance_all:
                if lambda_instance_all['failure_message'] != "":
                    data[0]['status']['failure_message'] = lambda_instance_all['failure_message']

            response['data'] = data
            return Response(response, status=status_code)
        elif filter == "info":
            data = [{
                "info": {
                    "id": lambda_instance_all['uuid'],
                    "name": lambda_instance_all['name'],
                    "instance_info": lambda_instance_all['instance_info']
                }}]

            response['data'] = data
            return Response(response, status=status_code)
        else:
            data = [{
                "info": {
                    "id": lambda_instance_all['uuid'],
                    "name": lambda_instance_all['name'],
                    "instance_info": lambda_instance_all['instance_info']
                },
                "status": {
                    "code": lambda_instance_all['code'],
                    "message": lambda_instance_all['status'],
                    "detail": lambda_instance_all['details']
                },
                "applications": lambda_instance_all['applications']
            }]

            # Add failure message only if it is not empty.
            if 'failure_message' in lambda_instance_all:
                if lambda_instance_all['failure_message'] != "":
                    data[0]['status']['failure_message'] = lambda_instance_all['failure_message']

            response['data'] = data
            return Response(response, status=status_code)

    def action(self, request, uuid, format=None):
        """
        This method is used to perform an action a specified lambda instance. Responds to POST
        requests on url r'^{prefix}/{lookup}{trailing_slash}$'
        """

        lambda_instance_uuid = uuid
        # Check if the specified lambda instance exists.
        lambda_instances = LambdaInstance.objects.filter(uuid=lambda_instance_uuid)
        if not lambda_instances.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['lambda_instance_not_found'])
        lambda_instance_data = LambdaInstanceSerializer(lambda_instances[0]).data

        action_parameter = request.data.get('action', '')

        # Check the current status of the lambda instance.
        if action_parameter == "start":
            if lambda_instance_data['status'] == LambdaInstance.STARTED:
                raise CustomAlreadyDoneError(CustomAlreadyDoneError
                                             .messages['lambda_instance_already']
                                             .format(state="started"))

            if lambda_instance_data['status'] != LambdaInstance.STOPPED and \
                   lambda_instance_data['status'] != LambdaInstance.FAILED:
                raise CustomCantDoError(CustomCantDoError.messages['cant_do'].
                                        format(action="start", object="a lambda instance",
                                               status=LambdaInstance.status_choices[
                                                   int(lambda_instance_data['status'])][1]))
        elif action_parameter == "stop":
            if lambda_instance_data['status'] == LambdaInstance.STOPPED:
                raise CustomAlreadyDoneError(CustomAlreadyDoneError
                                             .messages['lambda_instance_already']
                                             .format(state="stopped"))

            if lambda_instance_data['status'] != LambdaInstance.STARTED and \
                   lambda_instance_data['status'] != LambdaInstance.FAILED:
                raise CustomCantDoError(CustomCantDoError.messages['cant_do'].
                                        format(action="stop", object="a lambda instance",
                                               status=LambdaInstance.status_choices[
                                                   int(lambda_instance_data['status'])][1]))
        else:
            raise CustomParseError(CustomParseError.messages['action_value_error'])

        # Get the id of the master node and the ids of the slave nodes.
        master_id = None
        slave_ids = []

        servers = lambda_instance_data['servers']
        for server in servers:
            if server['pub_ip']:
                master_id = server['id']
            else:
                slave_ids.append(server['id'])

        # Create a task to perform the action on the lambda instance and an event to update the
        # database.
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        if action_parameter == "start":
            tasks.lambda_instance_start.delay(lambda_instance_data['uuid'], auth_url, auth_token,
                                              master_id, slave_ids)

            events.set_lambda_instance_status.delay(lambda_instance_data['uuid'],
                                                    LambdaInstance.STARTING)
        elif action_parameter == "stop":
            tasks.lambda_instance_stop.delay(lambda_instance_data['uuid'], auth_url, auth_token,
                                             master_id, slave_ids)

            events.set_lambda_instance_status.delay(lambda_instance_data['uuid'],
                                                    LambdaInstance.STOPPING)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({
            "status": {
                'code': status_code,
                'short_description': ResponseMessages.short_descriptions['lambda_instance_action']
            }}, status=status_code)

    def destroy(self, request, uuid, format=None):
        """
        This method is used to destroy a specified lambda instance. Responds to DELETE
        requests on url r'^{prefix}/{lookup}{trailing_slash}$'
        """

        # Check if the specified lambda instance exists.
        lambda_instances = LambdaInstance.objects.filter(uuid=uuid)
        if not lambda_instances.exists():
            raise CustomNotFoundError(CustomNotFoundError.messages['lambda_instance_not_found'])
        lambda_instance_data = LambdaInstanceSerializer(lambda_instances[0]).data

        # Check the current status of the lambda instance.
        if lambda_instance_data['status'] == LambdaInstance.DESTROYED:
            raise CustomAlreadyDoneError(CustomAlreadyDoneError
                                             .messages['lambda_instance_already']
                                             .format(state="destroyed"))

        if lambda_instance_data['status'] == LambdaInstance.CLUSTER_FAILED:
            raise CustomCantDoError(CustomCantDoError.messages['cant_do'].
                                        format(action="destroy", object="a lambda instance",
                                               status=LambdaInstance.status_choices[
                                                   int(lambda_instance_data['status'])][1]))

        # Get the id of the master node and the ids of the slave nodes.
        master_id = None
        public_ip_id = None
        slave_ids = []

        servers = lambda_instance_data['servers']
        for server in servers:
            if server['pub_ip']:
                master_id = server['id']
                public_ip_id = server['pub_ip_id']
            else:
                slave_ids.append(server['id'])

        # Create task to destroy the lambda instance.
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        # auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        tasks.lambda_instance_destroy.delay(lambda_instance_data['uuid'], auth_token,
                                            master_id, slave_ids, public_ip_id,
                                            lambda_instance_data['private_network'][0]['id'])

        # Create event to update the database.
        events.set_lambda_instance_status.delay(lambda_instance_data['uuid'],
                                                LambdaInstance.DESTROYING)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({
            "status": {
                'code': status_code,
                'short_description': ResponseMessages.short_descriptions['lambda_instance_destroy']
            }}, status=status_code)

    def parse_list_response(self, response):
        """
        This method is used to remove from a list response any fields that the serializer adds
        but are not wanted in a list response
        """

        wanted_fields = ['uuid', 'name', 'status', 'failure_message']
        unwanted_fields = set(LambdaInstanceSerializer.Meta.fields) - set(wanted_fields)

        for lambda_instance in response['data']:
            for unwanted_field in unwanted_fields:
                del lambda_instance[unwanted_field]

        response['status']['short_description'] = ResponseMessages.short_descriptions[
            'lambda_instances_list']

        for lambda_instance in response['data']:
            lambda_instance['status'] = {
                'code': lambda_instance['status'],
                'message': LambdaInstance.status_choices[int(lambda_instance['status'])][1],
                'detail': ResponseMessages.lambda_instance_status_details[
                    LambdaInstance.status_choices[int(lambda_instance['status'])][1]]
            }
            if lambda_instance['failure_message'] != "":
                lambda_instance['status']['failure_message'] = lambda_instance['failure_message']
            del lambda_instance['failure_message']

        # Change uuid name to id
        for item in response['data']:
            if 'uuid' in item:
                item['id'] = item['uuid']
                del item['uuid']

        return response


class CreateLambdaInstance(APIView):
    """
    Creates a new lambda instance
    """

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    parser_classes = (JSONParser,)

    def post(self, request, format=None):

        # Get okeanos authentication token
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        # Dynamically fetch the allowed values for the number of CPUs, the amount of RAM and the
        # size of the Disk for each VM.
        vm_parameter_values = get_vm_parameter_values(auth_url, auth_token)

        # Keep the vcpus values that are equal or greater than 2.
        vcpus = list()
        for value in vm_parameter_values['vcpus']:
            if value >= 2:
                vcpus.append(value)

        # Keep the ram values that are equal or greater that 2048.
        ram = list()
        for value in vm_parameter_values['ram']:
            if value >= 2048:
                ram.append(value)

        # Keep the disk values that are equal or greater than 10.
        disk = list()
        for value in vm_parameter_values['disk']:
            if value >= 10:
                disk.append(value)

        LambdaInstanceInfo.allowed['vcpus'] = vcpus
        LambdaInstanceInfo.allowed['ram'] = ram
        LambdaInstanceInfo.allowed['disk'] = disk

        # Parse request json into a custom serializer
        lambda_info = LambdaInstanceInfo(data=request.data)
        try:
            # Check Instance info validity
            lambda_info.is_valid(raise_exception=True)
        except ValidationError as exception:
            raise CustomValidationError(exception.detail)

        # Create the task that will handle the cluster creation
        create = tasks.create_lambda_instance.delay(lambda_info, auth_token)

        # Use the task uuid as the cluster uuid
        instance_uuid = create.id

        status_code = status.HTTP_202_ACCEPTED
        return Response({"status": {"code": status_code, "short_description":
                                                         ResponseMessages.short_descriptions[
                                                             'lambda_instance_create']
                                    },
                         "data": [{
                             "id": instance_uuid,
                             "links": {
                                 "self": (request.build_absolute_uri() +
                                          "{id}".format(id=instance_uuid)).replace("instance",
                                                                                   "instances")
                             }
                         }]}, status=status_code)
