import json
import uuid

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import resolve

from rest_framework import viewsets, status, mixins
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated

from rest_framework_xml.renderers import XMLRenderer

from fokia.utils import check_auth_token

from . import tasks, events
from .models import Application, LambdaInstance, LambdaInstanceApplicationConnection
from .exceptions import CustomParseError, CustomValidationError, CustomNotFoundError,\
    CustomAlreadyDoneError
from .serializers import ApplicationSerializer, LambdaInstanceSerializer
from .authenticate_user import KamakiTokenAuthentication


def authenticate(request):
    """
    Checks the validity of the authentication token of the user
    .. deprecated::
    Use authenticate_user.KamakiTokenAuthentication

    """

    # request.META contains all the headers of the request
    auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
    status, info = check_auth_token(auth_token)
    if status:
        status_code = status.HTTP_200_OK
        return Response({"data": [{"status": status_code,
                                   "result": "success"}]}, status=status_code)
    else:
        error_info = json.loads(info)['unauthorized']
        error_info['details'] = error_info.get('details') + 'unauthorized'

        status_code = status.HTTP_401_UNAUTHORIZED
        error_info['status'] = status_code
        return Response({"errors": [error_info]}, status=status_code)


class ApplicationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Implements the API calls relevant to application.
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
            lambda_instance = LambdaInstance.objects.filter(uuid=lambda_instance_uuid)
            if not lambda_instance.exists():
                raise CustomNotFoundError("The specified lambda instance does not exist.")

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

        return self._paginate_response(request)

    def create(self, request, format=None):
        """
        This method is used to upload an application to Pithos. Responds to POST requests on url
        r'^{prefix}{trailing_slash}$'
        """

        # Check if a file was sent with the request.
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            raise CustomParseError("No file uploaded.")

        # Check if another file with same name already exists.
        if self.get_queryset().filter(name=uploaded_file.name).count() > 0:
            raise CustomValidationError("File name already exists.")

        # Get the description provided with the request.
        description = request.data.get('description', '')

        # Get the name of the project provided.
        project_name = request.data.get('project_name', '')

        # Generate a uuid for the uploaded application.
        application_uuid = uuid.uuid4()

        # Create an event to insert a new entry on the database.
        events.create_new_application.delay(application_uuid, uploaded_file.name,
                                            self.pithos_container, description, request.user)

        # Create a task to upload the application from the local file system to Pithos.
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        tasks.upload_application_to_pithos.delay(auth_url, auth_token, self.pithos_container,
                                                 project_name, uploaded_file, application_uuid)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({"data": [{"status": status_code,
                                   "uuid": application_uuid,
                                   "result": "Accepted"}]}, status=status_code)

    def destroy(self, request, uuid, format=None):
        """
        This method is used to delete an application from Pithos. Responds to DELETE requests on
        url r'^{prefix}/{lookup}{trailing_slash}$'
        """

        # Check if the specified application exists.
        application = self.get_queryset().filter(uuid=uuid)
        if not application.exists():
            raise CustomNotFoundError("The specified application does not exist.")
        serializer = ApplicationSerializer(application)

        # Create task to delete the specified application from Pithos.
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        tasks.delete_application_from_pithos.delay(auth_url, auth_token, self.pithos_container,
                                                   serializer.data['name'], uuid)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({"data": [{"status": status_code,
                                   "result": "Accepted"}]}, status=status_code)

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
            raise CustomParseError("No lambda instance id provided.")

        # Check if the specified lambda instance exists.
        lambda_instance = LambdaInstance.objects.filter(uuid=lambda_instance_uuid)
        if not lambda_instance.exists():
            raise CustomNotFoundError("The specified lambda instance does not exist.")

        # Check if the specified application exists.
        application = self.get_queryset().filter(uuid=application_uuid)
        if not application.exists():
            raise CustomNotFoundError("The specified application does not exist.")

        # Check if the specified application is already deployed on the specified lambda instance.
        if LambdaInstanceApplicationConnection.objects.filter(lambda_instance=lambda_instance,
                                                              application=application).exists():
            raise CustomAlreadyDoneError("The specified application has already been deployed"
                                         " on the specified lambda instance.")

        # Create a task to deploy the application.
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        tasks.deploy_application.delay(auth_url, auth_token, self.pithos_container,
                                       lambda_instance_uuid, application_uuid)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({"data": [{"status": status_code,
                                   "result": "Accepted"}]}, status=status_code)

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
            raise CustomNotFoundError("The specified lambda instance does not exist.")

        return self._paginate_response(request)

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
            raise CustomParseError("No lambda instance id provided.")

        # Check if the specified lambda instance exists.
        lambda_instance = LambdaInstance.objects.filter(uuid=lambda_instance_uuid)
        if not lambda_instance.exists():
            raise CustomNotFoundError("The specified lambda instance does not exist.")

        # Check if the specified application exists.
        application = self.get_queryset().filter(uuid=application_uuid)
        if not application.exists():
            raise CustomNotFoundError("The specified application does not exist.")

        # Check if the specified application is already not deployed on the specified lambda
        # instance.
        if not LambdaInstanceApplicationConnection.objects.\
                filter(lambda_instance=lambda_instance, application=application).exists():
            raise CustomAlreadyDoneError("The specified application is already not deployed"
                                         " on the specified lambda instance.")

        # Create a task to withdraw the application.
        tasks.withdraw_application.delay(lambda_instance_uuid, application_uuid)

        # Return an appropriate response.
        status_code = status.HTTP_202_ACCEPTED
        return Response({"data": [{"status": status_code,
                                   "result": "Accepted"}]}, status=status_code)

    def _paginate_response(self, request):
        """
        This method is used to paginate a list response. The pagination method used is the default
        Django Rest Framework pagination.
        :param request: The request given to the calling view.
        :return: Returns the paginated response.
        """

        default_response = super(ApplicationViewSet, self).list(request)

        # Check if pagination was requested.
        if 'limit' in request.query_params:

            # Check if limit parameter is a positive integer.
            limit = request.query_params.get('limit')
            try:
                limit = int(limit)

                # Check if limit parameter is not a negative integer.
                if limit >= 0:
                    return self._parse_default_pagination_response(default_response)
                else:
                    raise CustomParseError("limit value should be a not negative integer.")
            except ValueError:
                raise CustomParseError("limit value should be a not negative integer.")
        else:
            return default_response

    def _parse_default_pagination_response(self, default_response):
        """
        This method is used to refactor the default response of the Django Rest Framework default
        pagination.
        :param default_response: The response that the default pagination returned.
        :return: The refactored response.
        """

        # Change the name or 'result' field to 'data'
        default_response.data['data'] = default_response.data['results']
        del default_response.data['results']

        # Add status field in response data.
        default_response.data['status'] = default_response.status_code

        return default_response


class LambdaInstanceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    queryset = LambdaInstance.objects.all()
    serializer_class = LambdaInstanceSerializer
    # Check the model field of uuid in models.py and define the regular expression that will be
    # used to parse the urls.
    lookup_field = 'uuid'

    # Answers only to GET requests on the url: r'^{prefix}{trailing_slash}$' (by default router).
    #def list(self, request, format=None):
    #    # Calculate pagination parameters and use them to retrieve the requested lambda instances.
    #    if 'limit' in request.query_params and 'page' in request.query_params:
    #        try:
    #            limit = int(request.query_params.get("limit"))
    #            page = int(request.query_params.get("page"))
    #        except (TypeError, ValueError):
    #            return Response({"errors": [{"message": "Bad parameter"}]},
    #                            status=status.HTTP_400_BAD_REQUEST)
    #
    #        if limit <= 0 or page <= 0:
    #            return Response({"errors":
    #                                 [{"message": "Zero or negative indexing not supported"}]},
    #                            status=status.HTTP_400_BAD_REQUEST)
    #        else:
    #            first_to_retrieve = (page - 1) * limit
    #            last_to_retrieve = page * limit
    #            serializer = LambdaInstanceSerializer(
    #                self.get_queryset()[first_to_retrieve:last_to_retrieve], many=True)
    #    elif 'limit' in request.query_params or 'page' in request.query_params:
    #            return Response({"errors": [{"message": "Missing parameter"}]},
    #                            status=status.HTTP_400_BAD_REQUEST)
    #    else:
    #            serializer = LambdaInstanceSerializer(self.get_queryset(), many=True)
    #
    #    wanted_fields = ['id', 'uuid', 'name']
    #    unwanted_fields = set(LambdaInstanceSerializer.Meta.fields) - set(wanted_fields)
    #
    #    lambda_instances_list = []
    #    # Remove unwanted fields from lambda instances information.
    #    for lambda_instance in serializer.data:
    #        for unwanted_field in unwanted_fields:
    #            del lambda_instance[unwanted_field]
    #        lambda_instances_list.append(lambda_instance)
    #
    #    return Response(lambda_instances_list, status=status.HTTP_200_OK)

    # Answers only to get requests on the url: r'^{prefix}/{lookup}{trailing_slash}$'
    # (by default router).
    def retrieve(self, request, uuid, format=None):
        """
        This method is used to get information about a specified lambda instance. Responds to GET
        requests on url r'^{prefix}/{lookup}{trailing_slash}$'
        """

        filter = request.query_params.get('filter', '')

        if filter == "status":
            return self.status(request, uuid)
        elif filter == "info":
            return self.details(request, uuid)
        elif filter == "":
            return Response("todo", status=200)
        else:
            raise CustomParseError("The input provided is invalid.")

    def details(self, request, uuid, format=None):
        """
        This method is used by retrieve method to get the details about a specified lambda
        instance.
        """

        # Check if the specified lambda instance exists.
        lambda_instance = LambdaInstance.objects.filter(uuid=uuid)
        if not lambda_instance.exists():
            raise CustomNotFoundError("The specified lambda instance does not exist.")
        serializer = LambdaInstanceSerializer(lambda_instance)

        wanted_fields = ['id', 'uuid', 'name', 'instance_info']
        unwanted_fields = set(LambdaInstanceSerializer.Meta.fields) - set(wanted_fields)

        lambda_instance = serializer.data
        # Remove unwanted fields from lambda instance information.
        for unwanted_field in unwanted_fields:
            del lambda_instance[unwanted_field]

        # Parse the instance info field.
        lambda_instance['instance_info'] = json.loads(lambda_instance['instance_info'])

        return Response(lambda_instance, status=status.HTTP_200_OK)

    def status(self, request, uuid, format=None):
        serializer = LambdaInstanceSerializer(get_object_or_404(self.get_queryset(), uuid=uuid))

        wanted_fields = ['id', 'uuid', 'name', 'status', 'failure_message']
        unwanted_fields = set(LambdaInstanceSerializer.Meta.fields) - set(wanted_fields)

        lambda_instance = serializer.data
        # Remove unwanted fields from lambda instance information.
        for unwanted_field in unwanted_fields:
            del lambda_instance[unwanted_field]

        return Response(lambda_instance, status=status.HTTP_200_OK)

    def action(self, request, uuid, format=None):
        action_parameter = request.data.get('action', '')

        if action_parameter == "start":
            return self.start(request, uuid)
        elif action_parameter == "stop":
            return self.stop(request, uuid)
        else:
            return Response("Bad Request", status=status.HTTP_400_BAD_REQUEST)

    def start(self, request, uuid, format=None):
        serializer = LambdaInstanceSerializer(get_object_or_404(self.get_queryset(), uuid=uuid))
        data = serializer.data

        # Check the current status of the lambda instance.
        if data['status'] == LambdaInstance.STARTED:
            return Response({"detail": "The specified lambda instance is already started"},
                            status=status.HTTP_400_BAD_REQUEST)

        if data['status'] != LambdaInstance.STOPPED and data['status'] != LambdaInstance.FAILED:
            return Response({"detail": "Cannot start lambda instance while current status " +
                             "is " + data['status']},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the id of the master node and the ids of the slave nodes.
        master_id = None
        slave_ids = []

        servers = data['servers']
        for server in servers:
            if server['pub_ip']:
                master_id = server['id']
            else:
                slave_ids.append(server['id'])

        # Create task to start the lambda instance.
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        tasks.lambda_instance_start.delay(data['uuid'], auth_url, auth_token, master_id,
                                          slave_ids)

        # Create event to update the database.
        events.set_lambda_instance_status.delay(data['uuid'], LambdaInstance.STARTING)

        return Response({"result": "Accepted"}, status=status.HTTP_202_ACCEPTED)

    def stop(self, request, uuid, format=None):
        serializer = LambdaInstanceSerializer(get_object_or_404(self.get_queryset(), uuid=uuid))
        data = serializer.data

        # Check the current status of the lambda instance.
        if data['status'] == LambdaInstance.STOPPED:
            return Response({"detail": "The specified lambda instance is already stopped"},
                            status=status.HTTP_400_BAD_REQUEST)

        if data['status'] != LambdaInstance.STARTED and data['status'] != LambdaInstance.FAILED:
            return Response({"detail": "Cannot stop lambda instance while current status " +
                             "is " + data['status']},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the id of the master node and the ids of the slave nodes.
        master_id = None
        slave_ids = []

        servers = data['servers']
        for server in servers:
            if server['pub_ip']:
                master_id = server['id']
            else:
                slave_ids.append(server['id'])

        # Create task to stop the lambda instance.
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        tasks.lambda_instance_stop.delay(data['uuid'], auth_url, auth_token, master_id,
                                         slave_ids)

        # Create event to update the database.
        events.set_lambda_instance_status.delay(data['uuid'], LambdaInstance.STOPPING)

        return Response({"result": "Accepted"}, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, uuid, format=None):
        serializer = LambdaInstanceSerializer(get_object_or_404(self.get_queryset(), uuid=uuid))
        data = serializer.data

        # Check the current status of the lambda instance.
        if data['status'] == LambdaInstance.DESTROYED:
            return Response({"detail": "The specified lambda instance is already destroyed"},
                            status=status.HTTP_400_BAD_REQUEST)

        if data['status'] != LambdaInstance.STARTED and \
            data['status'] != LambdaInstance.STOPPED and \
                data['status'] != LambdaInstance.FAILED:
            return Response({"detail": "Cannot destroy lambda instance while current status " +
                             "is " + data['status']},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the id of the master node and the ids of the slave nodes.
        master_id = None
        public_ip_id = None
        slave_ids = []

        servers = data['servers']
        for server in servers:
            if server['pub_ip']:
                master_id = server['id']
                public_ip_id = server['pub_ip_id']
            else:
                slave_ids.append(server['id'])

        # Create task to destroy the lambda instance.
        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

        tasks.lambda_instance_destroy.delay(data['uuid'], auth_url, auth_token, master_id,
                                            slave_ids, public_ip_id,
                                            data['private_network'][0]['id'])

        # Create event to update the database.
        events.set_lambda_instance_status.delay(data['uuid'], LambdaInstance.DESTROYING)

        return Response({"result": "Accepted"}, status=status.HTTP_202_ACCEPTED)


class CreateLambdaInstance(APIView):
    """
    Creates a new lambda instance
    """

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    parser_classes = (JSONParser,)

    def post(self, request, format=None):
        cluster_specs = request.data

        auth_token = request.META.get("HTTP_AUTHORIZATION").split()[-1]

        instance_name = cluster_specs['instance_name']
        master_name = cluster_specs['master_name']
        slaves = int(cluster_specs['slaves'])
        vcpus_master = int(cluster_specs['vcpus_master'])
        vcpus_slave = int(cluster_specs['vcpus_slave'])
        ram_master = int(cluster_specs['ram_master'])
        ram_slave = int(cluster_specs['ram_slave'])
        disk_master = int(cluster_specs['disk_master'])
        disk_slave = int(cluster_specs['disk_slave'])
        ip_allocation = cluster_specs['ip_allocation']
        network_request = int(cluster_specs['network_request'])
        project_name = cluster_specs['project_name']

        create = tasks.create_lambda_instance.delay(auth_token=auth_token,
                                                    instance_name=instance_name,
                                                    master_name=master_name,
                                                    slaves=slaves,
                                                    vcpus_master=vcpus_master,
                                                    vcpus_slave=vcpus_slave,
                                                    ram_master=ram_master,
                                                    ram_slave=ram_slave,
                                                    disk_master=disk_master,
                                                    disk_slave=disk_slave,
                                                    ip_allocation=ip_allocation,
                                                    network_request=network_request,
                                                    project_name=project_name)
        instance_uuid = create.id

        return Response({"uuid": instance_uuid}, status=202)
