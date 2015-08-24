from django.http import HttpResponse

from fokia.utils import check_auth_token


def authenticate(request):
    auth_token = request.META.get("HTTP_X_API_KEY")
    auth_url = request.META.get("HTTP_X_AUTH_URL")
    print auth_token, auth_url
    status, info = check_auth_token(auth_token, auth_url=auth_url)
    if status:
        return HttpResponse("Success \n{}".format(info), status=200)
    else:
        return HttpResponse("Unauthorized Access \n{}".format(info), status=401)
