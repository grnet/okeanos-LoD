import json
from os import path, mkdir

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings

from rest_framework.permissions import IsAuthenticated

from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from rest_framework_xml.renderers import XMLRenderer

from fokia.utils import check_auth_token
from .models import ProjectFile, LambdaInstance
from .authenticate_user import KamakiTokenAuthentication
from .serializers import ProjectFileSerializer


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
                                   "code": 500,
                                   "details": ""}]}, status=500)

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
