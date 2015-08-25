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
    # TODO
    # Make sure user passed authentication.

    try:
        limit = int(request.GET.get("limit"))
        page = int(request.GET.get("page"))

        if limit <= 0 or page <= 0:
          return JsonResponse({"errors": "Zero or negative indexing is not supported"}, status=500)

        # Retrieve Lambda Instances from the database.
        first_to_retrieve = (page - 1) * limit
        last_to_retrieve = page * limit

        database_instances = LambdaInstance.objects.all()[first_to_retrieve:last_to_retrieve]
    except:
        database_instances = LambdaInstance.objects.all()

    if len(database_instances) == 0:
      return JsonResponse({"errors": "No instances found"}, status=404)

    instances_list = []
    for database_instance in database_instances:
      instances_list.append({"name": database_instance.name,
                             "id": database_instance.id,
                             "uuid": database_instance.uuid})

    return JsonResponse({"lambda-instances": instances_list}, status=200)

def lambda_instance_details(request, instance_uuid):
    # TODO
    # Make sure user passed authentication.

    # Retrieve specified Lambda Instance.
    try:
        database_instance = LambdaInstance.objects.get(uuid=instance_uuid)
    except:
        return JsonResponse({"errors": "Lambda instance not found"}, status=404)

    return JsonResponse({"name": database_instance.name,
                         "id": database_instance.id,
                         "uuid": database_instance.uuid,
                         "details": json.loads(database_instance.instance_info)}, status=200)

def lambda_instance_status(request, instance_uuid):
    # TODO
    # Make sure user passed authentication.

    # Retrieve specified Lambda Instance.
    try:
        database_instance = LambdaInstance.objects.get(uuid=instance_uuid)
    except:
        return JsonResponse({"errors": "Lambda instance not found"}, status=404)

    return JsonResponse({"name": database_instance.name,
                         "status": LambdaInstance.status_choices[int(database_instance.status) - 1][1]}, status=200)
