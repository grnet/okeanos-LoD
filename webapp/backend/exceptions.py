from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException

class CustomAuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Unauthorized. Request failed because user provided an invalid token."


class CustomParseError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Parse error."


class CustomValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation Error."


class CustomNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Not Found."


class CustomAlreadyDoneError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Already Done."


custom_exceptions = (CustomAuthenticationFailed, CustomParseError, CustomValidationError,
                     CustomNotFoundError, CustomAlreadyDoneError)

def parse_custom_exception(default_response):
    response = {}

    response['status'] = default_response.status_code
    # response['code'] =
    response['detail'] = default_response.data['detail']

    response_status = default_response.status_code
    return Response({"errors": [response]}, response_status)

def custom_exception_handler(exc, context):

    default_response = exception_handler(exc, context)

    if isinstance(exc, custom_exceptions):
        return parse_custom_exception(default_response)

    return default_response
