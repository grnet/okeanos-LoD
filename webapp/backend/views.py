import json

from os import path, mkdir

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings

from rest_framework.permissions import IsAuthenticated

from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.parsers import JSONParser

from rest_framework_xml.renderers import XMLRenderer

from django.views.decorators.csrf import csrf_exempt

from django.utils.datastructures import SortedDict
from fokia.utils import check_auth_token
from .models import ProjectFile, LambdaInstance, Server, PrivateNetwork
from .authenticate_user import KamakiTokenAuthentication
from .serializers import ProjectFileSerializer

import tasks
import events


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


def list_lambda_instances(request):
    """
    Lists the lambda instances owned by the user.
    """

    # Verify that the request method is GET.
    if request.method != 'GET':
        return JsonResponse({"errors":
                             [{"message": "",
                               "code": 400,
                               "details": ""}]}, status=400)

    # Authenticate user.
    authentication_response = authenticate(request)
    if authentication_response.status_code != 200:
        return authentication_response

    # Parse limit and page parameters.
    try:
        limit = int(request.GET.get("limit"))
        page = int(request.GET.get("page"))

        if limit <= 0 or page <= 0:
            return JsonResponse({"errors":
                                 [{"message": "Zero or negative indexing is not supported",
                                   "code": 400,
                                   "details": ""}]}, status=400)

        # Retrieve the lambda instances from the database.
        first_to_retrieve = (page - 1) * limit
        last_to_retrieve = page * limit
        database_instances = LambdaInstance.objects.all()[first_to_retrieve:last_to_retrieve]
    except:
        database_instances = LambdaInstance.objects.all()

    if len(database_instances) == 0:
        return JsonResponse({"errors": [{"message": "No instances found",
                                         "code": 404,
                                         "details": ""}]}, status=404)

    instances_list = []
    for database_instance in database_instances:
        instances_list.append({"name": database_instance.name,
                               "id": database_instance.id,
                               "uuid": database_instance.uuid})

    return JsonResponse({"data": instances_list}, status=200)


def lambda_instance_details(request, instance_uuid):
    """
    Returns the details for a specific lambda instance owned by the user.
    """

    # Verify that the request method is GET.
    if request.method != 'GET':
        return JsonResponse({"errors":
                             [{"message": "",
                               "code": 400,
                               "details": ""}]}, status=400)

    # Authenticate user.
    authentication_response = authenticate(request)
    if authentication_response.status_code != 200:
        return authentication_response

    # Retrieve specified Lambda Instance.
    try:
        database_instance = LambdaInstance.objects.get(uuid=instance_uuid)
    except:
        return JsonResponse({"errors": [{"message": "Lambda instance not found",
                                         "code": 404,
                                         "details": ""}]}, status=404)

    return JsonResponse({"data": {"name": database_instance.name,
                                  "id": database_instance.id,
                                  "uuid": database_instance.uuid,
                                  "details": json.loads(database_instance.instance_info)}},
                        status=200)


def lambda_instance_status(request, instance_uuid):
    """
    Returns the status of a specified lambda instance owned by the user.
    """

    # Verify that the request method is GET.
    if request.method != 'GET':
        return JsonResponse({"errors":
                             [{"message": "",
                               "code": 400,
                               "details": ""}]}, status=400)

    # Authenticate user.
    authentication_response = authenticate(request)
    if authentication_response.status_code != 200:
        return authentication_response

    # Retrieve specified Lambda Instance.
    try:
        database_instance = LambdaInstance.objects.get(uuid=instance_uuid)
    except:
        return JsonResponse({"errors": [{"message": "Lambda instance not found",
                                         "code": 404,
                                         "details": ""}]}, status=404)

    return JsonResponse({"data": {"name": database_instance.name,
                                  "status": LambdaInstance.
                        status_choices[int(database_instance.status)][1],
                                  "failure_message": database_instance.failure_message,
                                  "uuid": database_instance.uuid,
                                  "id": database_instance.id}}, status=200)


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


@csrf_exempt
def lambda_instance_start(request, instance_uuid):
    """
    Starts a specific lambda instance owned by the user.
    """

    # Verify that the request method is POST.
    if request.method != 'POST':
        return JsonResponse({"errors":
                             [{"message": "",
                               "code": 400,
                               "details": ""}]}, status=400)

    # Authenticate user.
    authentication_response = authenticate(request)
    if authentication_response.status_code != 200:
        return authentication_response

    # Check if the specified lambda instance exists.
    if not LambdaInstance.objects.filter(uuid=instance_uuid).exists():
        return JsonResponse({"errors": [{"message": "Lambda instance not found",
                                         "code": 404,
                                         "details": ""}]}, status=404)

    # Check the current status of the lambda instance.
    database_instance = LambdaInstance.objects.get(uuid=instance_uuid)

    if database_instance.status == LambdaInstance.STARTED:
        return JsonResponse({"errors":
                             [{"message": "The specified lambda instance is already started",
                               "code": 400,
                               "details": ""}]}, status=400)

    if database_instance.status != LambdaInstance.STOPPED and \
            LambdaInstance.FAILED != database_instance.status:
        return JsonResponse({"errors":
                             [{"message": "Cannot start lambda instance while current " +
                                          "status is " + LambdaInstance.status_choices[
                                              int(database_instance.status)][1],
                               "code": 400,
                               "details": ""}]}, status=400)

    # Get the ids of the servers of the specified lambda instance.
    instance_servers = Server.objects.filter(lambda_instance=database_instance)
    master_id = instance_servers.exclude(pub_ip=None).values('id')[0]['id']
    slaves = instance_servers.filter(pub_ip=None).values('id')
    slave_ids = []
    for slave in slaves:
        slave_ids.append(slave['id'])

    # Create task to start the lambda instance.
    auth_token = request.META.get("HTTP_X_API_KEY")
    auth_url = request.META.get("HTTP_X_AUTH_URL")
    if not auth_url:
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

    tasks.lambda_instance_start.delay(instance_uuid, auth_url, auth_token, master_id, slave_ids)

    # Create event to update the database.
    events.set_lambda_instance_status.delay(instance_uuid, LambdaInstance.STARTING)

    return JsonResponse({"result": "Accepted"}, status=202)


@csrf_exempt
def lambda_instance_stop(request, instance_uuid):
    """
    Stops a specific lambda instance owned by the user.
    """

    # Verify that the request method is POST.
    if request.method != 'POST':
        return JsonResponse({"errors":
                             [{"message": "",
                               "code": 400,
                               "details": ""}]}, status=400)

    # Authenticate user.
    authentication_response = authenticate(request)
    if authentication_response.status_code != 200:
        return authentication_response

    # Check if the specified lambda instance exists.
    if not LambdaInstance.objects.filter(uuid=instance_uuid).exists():
        return JsonResponse({"errors": [{"message": "Lambda instance not found",
                                         "code": 404,
                                         "details": ""}]}, status=404)

    # Check the current status of the lambda instance.
    database_instance = LambdaInstance.objects.get(uuid=instance_uuid)

    if database_instance.status == LambdaInstance.STOPPED:
        return JsonResponse({"errors":
                             [{"message": "The specified lambda instance is already stopped",
                               "code": 400,
                               "details": ""}]}, status=400)

    if database_instance.status != LambdaInstance.STARTED and \
                    database_instance.status != LambdaInstance.FAILED:
        return JsonResponse({"errors":
                             [{"message": "Cannot stop lambda instance while current " +
                                          "status is " + LambdaInstance.status_choices[
                                              int(database_instance.status)][1],
                               "code": 400,
                               "details": ""}]}, status=400)

    # Get the ids of the servers of the specified lambda instance.
    instance_servers = Server.objects.filter(lambda_instance=LambdaInstance.objects.get(
        uuid=instance_uuid))
    master_id = instance_servers.exclude(pub_ip=None).values('id')[0]['id']
    slaves = instance_servers.filter(pub_ip=None).values('id')
    slave_ids = []
    for slave in slaves:
        slave_ids.append(slave['id'])

    # Create task to stop the lambda instance.
    auth_token = request.META.get("HTTP_X_API_KEY")
    auth_url = request.META.get("HTTP_X_AUTH_URL")
    if not auth_url:
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

    tasks.lambda_instance_stop.delay(instance_uuid, auth_url, auth_token, master_id, slave_ids)

    # Create event to update the database.
    events.set_lambda_instance_status.delay(instance_uuid, LambdaInstance.STOPPING)

    return JsonResponse({"result": "Accepted"}, status=202)


@csrf_exempt
def lambda_instance_destroy(request, instance_uuid):
    """
    Destroys a specific lambda instance owned by the user.
    """

    # Verify that the request method is POST.
    if request.method != 'POST':
        return JsonResponse({"errors":
                             [{"message": "",
                               "code": 400,
                               "details": ""}]}, status=400)

    # Authenticate user.
    authentication_response = authenticate(request)
    if authentication_response.status_code != 200:
        return authentication_response

    # Check if the specified lambda instance exists.
    if not LambdaInstance.objects.filter(uuid=instance_uuid).exists():
        return JsonResponse({"errors": [{"message": "Lambda instance not found",
                                         "code": 404,
                                         "details": ""}]}, status=404)

    # Check the current status of the lambda instance.
    database_instance = LambdaInstance.objects.get(uuid=instance_uuid)

    if database_instance.status == LambdaInstance.DESTROYED:
        return JsonResponse({"errors":
                             [{"message": "The specified lambda instance is already destroyed",
                               "code": 400,
                               "details": ""}]}, status=400)

    if database_instance.status != LambdaInstance.STARTED and \
                    LambdaInstance.STOPPED != database_instance.status and \
                    LambdaInstance.FAILED != database_instance.status:
        return JsonResponse({"errors":
                             [{"message": "Cannot destroy lambda instance while current " +
                                          "status is " + LambdaInstance.status_choices[
                                              int(database_instance.status)][1],
                               "code": 400,
                               "details": ""}]}, status=400)

    # Get the ids of the servers of the specified lambda instance.
    instance_servers = Server.objects.filter(lambda_instance=LambdaInstance.objects.get(
        uuid=instance_uuid))
    master_id = instance_servers.exclude(pub_ip=None).values('id')[0]['id']
    slaves = instance_servers.filter(pub_ip=None).values('id')
    slave_ids = []
    for slave in slaves:
        slave_ids.append(slave['id'])

    public_ip_id = instance_servers.exclude(pub_ip=None).values('pub_ip_id')[0]['pub_ip_id']

    private_network_id = PrivateNetwork.objects.get(lambda_instance=LambdaInstance.objects.get(
        uuid=instance_uuid)).id

    # Create task to destroy the lambda instance.
    auth_token = request.META.get("HTTP_X_API_KEY")
    auth_url = request.META.get("HTTP_X_AUTH_URL")
    if not auth_url:
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

    tasks.lambda_instance_destroy.delay(instance_uuid, auth_url, auth_token, master_id, slave_ids,
                                        public_ip_id, private_network_id)

    # Create event to update the database.
    events.set_lambda_instance_status.delay(instance_uuid, LambdaInstance.DESTROYING)

    return JsonResponse({"result": "Accepted"}, status=202)


def create_lambda_instance(request):
    """
    Creates a new lambda instance
    """

    # Authenticate user
    authentication_response = authenticate(request)
    if authentication_response.status_code != 200:
        return authentication_response

    # request.META contains all the headers of the request
    auth_token = request.META.get("HTTP_X_API_KEY")
    auth_url = request.META.get("HTTP_X_AUTH_URL")
    cloud_name = request.META.get('HTTP_CLOUD_NAME')
    master_name = request.META.get('HTTP_MASTER_NAME')
    slaves = int(request.META.get('HTTP_SLAVES'))
    vcpus_master = int(request.META.get('HTTP_VCPUS_MASTER'))
    vcpus_slave = int(request.META.get('HTTP_VCPUS_SLAVE'))
    ram_master = int(request.META.get('HTTP_RAM_MASTER'))
    ram_slave = int(request.META.get('HTTP_RAM_SLAVE'))
    disk_master = int(request.META.get('HTTP_DISK_MASTER'))
    disk_slave = int(request.META.get('HTTP_DISK_SLAVE'))
    ip_allocation = request.META.get('HTTP_IP_ALLOCATION')
    network_request = int(request.META.get('HTTP_NETWORK_REQUEST'))
    project_name = request.META.get('HTTP_PROJECT_NAME')

    tasks.create_lambda_instance.delay(auth_token=auth_token,
                                       auth_url=auth_url,
                                       cloud_name=cloud_name,
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

    # return HttpResponse("Creating cluster")

    specs = SortedDict([('master_name', master_name), ('slaves', slaves),
                        ('vcpus_master', vcpus_master), ('vcpus_slave', vcpus_slave),
                        ('ram_master', ram_master), ('ram_slave', ram_slave),
                        ('disk_master', disk_master), ('disk_slave', disk_slave),
                        ('ip_allocation', ip_allocation), ('network_request', network_request),
                        ('project_name', project_name)])

    return JsonResponse({"specs": specs}, status=200)

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

        tasks.create_lambda_instance.delay(auth_token=auth_token,
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

        # return HttpResponse("Creating cluster")

        specs = SortedDict([('master_name', master_name), ('slaves', slaves),
                            ('vcpus_master', vcpus_master), ('vcpus_slave', vcpus_slave),
                            ('ram_master', ram_master), ('ram_slave', ram_slave),
                            ('disk_master', disk_master), ('disk_slave', disk_slave),
                            ('ip_allocation', ip_allocation), ('network_request', network_request),
                            ('project_name', project_name)])

        # return JsonResponse({"specs": specs}, status=200)

        return Response({"specs": specs}, status=200)
