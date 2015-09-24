from rest_framework import viewsets
from rest_framework import status as rest_status
from rest_framework import generics, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from .models import LambdaInstance, LambdaApplication, User, Token
from .serializers import (UserSerializer, LambdaInstanceSerializer, LambdaApplicationSerializer)
# from .serializers import LambdaInstanceInfo
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.parsers import JSONParser

from .authenticate_user import KamakiTokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .exceptions import CustomParseError, CustomValidationError, CustomNotFoundError,\
    CustomAlreadyDoneError, CustomCantDoError

from .response_messages import ResponseMessages
import events

from django.conf import settings

# Create your views here.

# def authenticate(request):
#     user_auth_token = request.META.get('HTTP_AUTHORIZATION').split()[1]
#     token_obj= list(Token.objects.filter(key=user_auth_token))[0]
#     user = list(User.objects.filter(kamaki_token=token_obj))[0]
#     # if it does not exist, create them


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for viewing Users.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

class LambdaInstanceView(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin, # debugging
                         viewsets.GenericViewSet):
    """
    APIView for viewing lambda instances
    """
    queryset = LambdaInstance.objects.all()
    serializer_class = LambdaInstanceSerializer
    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer
    parser_classes = (JSONParser,)

    lookup_field = 'uuid'

    # @detail_route(methods=['post'], url_path="foo")
    # def foo(self, request, *args, **kwargs):
    #     """
    #     Debug method for testing things. TODO: Delete it.
    #     :param request:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     # data = request.data
    #     user_auth = request.auth
    #     user = request.user # this is the authenticated user.
    #
    #     user_headers = request.META['HTTP_AUTHORIZATION'].split()[-1]
    #
    #     response = Response({"user": str(user)}, status=201)
    #     return response

    def create(self, request, *args, **kwargs):
        """
        Create api call for lambda_instance.
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

        # Parse request json into a custom serializer
        # lambda_info = LambdaInstanceInfo(data=request.data)
        # try:
        #     # Check Instance info validity
        #     lambda_info.is_valid(raise_exception=True)
        # except ValidationError as exception:
        #     raise CustomValidationError(exception.detail)

        create_event = events.createLambdaInstance.delay(uuid, instance_name, instance_info, owner, status,
                                                         failure_message)

        status_code = rest_status.HTTP_202_ACCEPTED
        if settings.DEBUG:
            return Response({"status": {"code": status_code,
                                   "short_description": ResponseMessages.short_descriptions[
                                       'lambda_instance_create']},
                         "data": [
                             {"id": uuid}
                         ],
                         "debug": create_event.status
                         }, status=status_code)
        else:
            return Response({"status": {"code": status_code,
                                   "short_description": ResponseMessages.short_descriptions[
                                       'lambda_instance_create']},
                         "data": [
                             {"id": uuid}
                         ],}, status=status_code)

    @detail_route(methods=['post'], url_path="status")
    def updateStatus(self, request, uuid, *args, **kwargs):
        data = request.data

        status = data['status']
        failure_message = data['failure_message'] if 'failure_message' in data else None
        update_event = events.updateLambdaInstanceStatus.delay(uuid, status, failure_message)

        status_code = rest_status.HTTP_202_ACCEPTED

        if settings.DEBUG:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                                       'lambda_instance_update']},
                "data": [{"id": uuid}],
                "debug": update_event.status,
            }, status=status_code)
        else:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                                       'lambda_instance_update']},
                "data": [{"id": uuid}],
            }, status=status_code)

    def destroy(self, request, uuid, *args, **kwargs):
        destroy_event = events.deleteLambdaInstance.delay(uuid)

        status_code = rest_status.HTTP_202_ACCEPTED

        if settings.DEBUG:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                                       'lambda_instance_destroy']},
                "data": [{"id": uuid},],
                "debug": destroy_event.status,
            }, status=status_code)
        else:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                                       'lambda_instance_destroy']},
                "data": [{"id": uuid},],
            }, status=status_code)



class LambdaInstanceCounterView(APIView):

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    def get(self, request, format=None):
        return Response({"count": str(LambdaInstance.objects.count())},
                        status=200)

class LambdaApplicationView(mixins.ListModelMixin, # debugging
                            mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):

    queryset = LambdaApplication.objects.all()
    serializer_class = LambdaApplicationSerializer
    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    lookup_field = 'uuid'

    def create(self, request, *args, **kwargs):
        """
        Create api call for lambda_application.
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

        create_event = events.createLambdaApplication.delay(
            uuid, status=status, name=name, description=description,
            owner=owner, failure_message=failure_message
        )

        status_code = rest_status.HTTP_202_ACCEPTED

        if settings.DEBUG:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                                       'lambda_application_create']},
                "debug": create_event.status,
                "data": [{"id": uuid},],
            }, status=status_code)
        else:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                                       'lambda_application_create']},
                "data": [{"id": uuid},],
            }, status=status_code)

    @detail_route(methods=['post'], url_path="status")
    def updateStatus(self, request, uuid, *args, **kwargs):
        data = request.data
        status = data['status']
        failure_message = data['failure_message'] if 'failure_message' in data else None
        update_event = events.updateLambdaApplicationStatus.delay(uuid, status, failure_message)

        status_code = rest_status.HTTP_202_ACCEPTED


        if settings.DEBUG:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                                       'lambda_application_update']},
                "data": [{"id": uuid}],
                "debug": update_event.status,
            }, status=status_code)
        else:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                                       'lambda_application_update']},
                "data": [{"id": uuid}],
            }, status=status_code)

    def destroy(self, request, uuid, *args, **kwargs):
        destroy_event = events.deleteLambdaApplication.delay(uuid)

        status_code = rest_status.HTTP_202_ACCEPTED

        if settings.DEBUG:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                                       'lambda_application_destroy']},
                "data": [{"id": uuid},],
                "debug": destroy_event.status,
            }, status=status_code)
        else:
            return Response({
                "status": {"code": status_code,
                           "short_description": ResponseMessages.short_descriptions[
                                       'lambda_application_destroy']},
                "data": [{"id": uuid},],
            }, status=status_code)



class LambdaApplicationCounterView(APIView):

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    def get(self, request, format=None):
        return Response({"count": str(LambdaApplication.objects.count())},
                        status=200)