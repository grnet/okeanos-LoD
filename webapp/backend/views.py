<<<<<<< HEAD
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
    # Retrieve token from HTTP Header.
    #token = request.META['HTTP_TOKEN']

    #TODO
    # Make sure user passed authentication.

    # Retrieve Lambda Instances' uuids from the database.
    instances = LambdaInstance.objects.all()

    i = 1
    result = {}
    for instance in instances:
      new_key = "Lambda Instance {number}".format(number = i)
      result[new_key] = instance.uuid
      i = i + 1

    result = collections.OrderedDict(sorted(result.items()))

    return JsonResponse(result, status=200)
