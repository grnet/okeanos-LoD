from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework import generics, mixins
from rest_framework.views import APIView
from .models import LambdaInstance, LambdaApplication, User, Token
from .serializers import UserSerializer, LambdaInstanceSerializer, LambdaApplicationSerializer
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_xml.renderers import XMLRenderer

from .authenticate_user import KamakiTokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.

def authenticate(request):
    user_auth_token = request.META.get('HTTP_AUTHORIZATION').split()[1]
    token_obj= list(Token.objects.filter(key=user_auth_token))[0]
    user = list(User.objects.filter(kamaki_token=token_obj))[0]
    # if it does not exist, create them


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for viewing Users.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

class LambdaInstanceView(mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
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

    @detail_route(methods=['post'], url_path="foo")
    def foo(self, request, *args, **kwargs):
        """
        Debug method for testing things. TODO: Delete it.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data
        user_auth = request.auth
        user = request.user # this is the authenticated user.

        user_headers = request.META['HTTP_AUTHORIZATION'].split()[-1]

        response = Response({"user": str(user)}, status=201)
        return response

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
        failure_message = data['failure_message']
        status = data['status']

        # TODO: Create celery task to write to the database
        raise NotImplementedError

        # owner = user
        #
        # li = LambdaInstance(uuid = uuid, name = instance_name,
        #               status = status, instance_info = instance_info,
        #               owner = owner, failure_message = failure_message,
        #               )
        # li.save()

        return Response()

class LambdaInstanceCounterView(APIView):

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    def get(self, request, format=None):
        return Response({"count": str(LambdaInstance.objects.count())},
                        status=200)

class LambdaApplicationView(mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin, # debugging
                            viewsets.GenericViewSet):

    queryset = LambdaApplication.objects.all()
    serializer_class = LambdaApplicationSerializer
    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    def create(self, request, *args, **kwargs):
        """
        Create api call for lambda_application.
        :param request: The HTTP POST request making the call.
        :param args:
        :param kwargs:
        :return: A response object according to the outcome of the call.
        """
        data = request.data

        lambda_app_description = data['description']
        lambda_instance_uuid = data['lambda_instance_uuid']

        # TODO: Create celery task to write to the database
        raise NotImplementedError

        return Response()

class LambdaApplicationCounterView(APIView):

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    def get(self, request, format=None):
        return Response({"count": str(LambdaApplication.objects.count())},
                        status=200)