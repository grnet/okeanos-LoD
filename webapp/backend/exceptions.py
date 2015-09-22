"""
This file includes all the custom made exceptions. These exceptions are thrown by the API and
used to override the structure of the response messages.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, ValidationError


class CustomAuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Unauthorized. Request failed because user provided an invalid token."


class CustomParseError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Parse error."

    messages = {
        'no_file_error': "No file uploaded.",
        'no_lambda_instance_id_error': "No lambda instance id provided.",
        'limit_value_error': "limit value should be an integer greater or equal to zero.",
        'filename_already_exists_error': "The specified file name already exists.",
        'filter_value_error': "filter GET parameter can be used with values status or info.",
        'action_value_error': "action POST parameter can be used with start or stop value."
    }


class CustomValidationError(ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation Error."


class CustomNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Not Found."

    messages = {
        'lambda_instance_not_found': "The specified lambda instance doesn't exist.",
        'application_not_found': "The specified application doesn't exist."
    }


class CustomAlreadyDoneError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Already Done."

    messages = {
        'application_already_deployed': "The specified application has already been deployed on the"
                                        " specified lambda instance.",
        'application_not_deployed': "The specified application has not been deployed on the "
                                    "specified lambda instance.",
        'lambda_instance_already': "The specified lambda instance is already {state}."

    }


class CustomCantDoError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Can't do."

    messages = {
        'cant_do': "Can't {action} {object} while lambda instance status is {status}."
    }


custom_exceptions = (CustomAuthenticationFailed, CustomParseError, CustomValidationError,
                     CustomNotFoundError, CustomAlreadyDoneError, CustomCantDoError)


def parse_custom_exception(exception, default_response):
    response = dict({'errors': []})

    if isinstance(exception, CustomValidationError):
        for key, values in default_response.data.items():
            detail = []
            for value in values:
                detail.append("{key}: {value}".format(key=key, value=value))

            response['errors'].append({'status': default_response.status_code,
                                       'detail': detail})
    else:
        for key, value in default_response.data.items():
            response['errors'].append({'status': default_response.status_code,
                                       'detail': value})

    response_status = default_response.status_code
    return Response(response, response_status)


def custom_exception_handler(exc, context):

    default_response = exception_handler(exc, context)

    if isinstance(exc, custom_exceptions):
        return parse_custom_exception(exc, default_response)

    return default_response
