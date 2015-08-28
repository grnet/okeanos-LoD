from django.http import JsonResponse
import json
from fokia.utils import check_auth_token

from .models import LambdaInstance

def authenticate(request):
    """
    Checks the validity of the authentication token of the user
    """

    # request.META contains all the headers of the request
    auth_token = request.META.get("HTTP_X_API_KEY")
    auth_url = request.META.get("HTTP_X_AUTH_URL")
    print auth_token, auth_url
    status, info = check_auth_token(auth_token, auth_url=auth_url)
    if status:
        return JsonResponse({"result": "Success"}, status=200)
    else:
        return JsonResponse({"errors": [json.loads(info)]}, status=401)


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
