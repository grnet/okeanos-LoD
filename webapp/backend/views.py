import json
from os import path, mkdir

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated

from rest_framework_xml.renderers import XMLRenderer

from fokia.utils import check_auth_token

from . import tasks, events
from .models import ProjectFile, LambdaInstance
from .serializers import ProjectFileSerializer, LambdaInstanceSerializer
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
        return JsonResponse({"result": "success"}, status=200)
    else:
        error_info = json.loads(info)['unauthorized']
        error_info['details'] = error_info.get('details') + 'unauthorized'
        return JsonResponse({"errors": [error_info]}, status=401)


class ProjectFileList(APIView):
    """
    List uploaded files, upload a file to the users folder.
    """

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    renderer_classes = JSONRenderer, XMLRenderer, BrowsableAPIRenderer

    def get(self, request, format=None):
        files = ProjectFile.objects.filter(owner=request.user)
        file_serializer = ProjectFileSerializer(files, many=True)
        return Response(file_serializer.data, status=200, content_type=format)

    def put(self, request, format=None):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"errors": [{"message": "No file uploaded", "code": 422}]}, status=422)
        description = request.data.get('description', '')
        new_file_path = path.join(settings.FILE_STORAGE, uploaded_file.name)
        if not path.exists(settings.FILE_STORAGE):
            mkdir(settings.FILE_STORAGE)
        with open(new_file_path, 'wb+') as f:
            f.write(uploaded_file.read())
        if path.isfile(new_file_path):
            # TODO: Change this to an event call that updates the db
            ProjectFile.objects.create(name=uploaded_file.name,
                                       path=new_file_path,
                                       description=description,
                                       owner=request.user)
        return Response({"result": "success"}, status=201)

    def delete(self, request, format=None):
        file_id = request.data.get('id')
        if not file_id:
            return Response({"errors:"[{"message": "missing id header", "code": 422}]},
                            status=422)
        try:
            file_data = ProjectFile.objects.get(id=file_id)
        except ProjectFile.DoesNotExist:
            return Response({"errors:"[{"message": "file does not exist", "code": 400}]},
                            status=400)

        if file_data.owner != request.user:
            return Response({"errors:"[{"message": "file does not exist", "code": 400}]},
                            status=400)
        # TODO: Change this to an event call that update the db
        file_data.delete()
        return Response({"result": "success"}, status=200)


class LambdaInstanceViewSet(viewsets.ReadOnlyModelViewSet):

    authentication_classes = KamakiTokenAuthentication,
    permission_classes = IsAuthenticated,
    queryset = LambdaInstance.objects.all()
    serializer_class = LambdaInstanceSerializer

    def list(self, request, format=None):
        serializer = LambdaInstanceSerializer(self.queryset, many=True)

        wanted_fields = ['id', 'uuid', 'name']
        unwanted_fields = set(LambdaInstanceSerializer.Meta.fields) - set(wanted_fields)

        lambda_instances_list = []
        for lambda_instance in serializer.data:
            for unwanted_field in unwanted_fields:
                del lambda_instance[unwanted_field]
            lambda_instances_list.append(lambda_instance)

        return Response(lambda_instances_list)

    def retrieve(self, request, pk, format=None):
        serializer = LambdaInstanceSerializer(get_object_or_404(self.queryset, uuid=pk))

        wanted_fields = ['id', 'uuid', 'name', 'instance_info']
        unwanted_fields = set(LambdaInstanceSerializer.Meta.fields) - set(wanted_fields)

        lambda_instance = serializer.data
        for unwanted_field in unwanted_fields:
            del lambda_instance[unwanted_field]

        return Response(lambda_instance)

    @detail_route(methods=['get'])
    def status(self, request, pk, format=None):
        serializer = LambdaInstanceSerializer(get_object_or_404(self.queryset, uuid=pk))

        wanted_fields = ['id', 'uuid', 'name', 'status', 'failure_message']
        unwanted_fields = set(LambdaInstanceSerializer.Meta.fields) - set(wanted_fields)

        lambda_instance = serializer.data
        for unwanted_field in unwanted_fields:
            del lambda_instance[unwanted_field]

        return Response(lambda_instance)

    @detail_route(methods=['post'])
    def start(self, request, pk, format=None):
        serializer = LambdaInstanceSerializer(get_object_or_404(self.queryset, uuid=pk))
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

    @detail_route(methods=['post'])
    def stop(self, request, pk, format=None):
        serializer = LambdaInstanceSerializer(get_object_or_404(self.queryset, uuid=pk))
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

    def destroy(self, request, pk, format=None):
        serializer = LambdaInstanceSerializer(get_object_or_404(self.queryset, uuid=pk))
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

