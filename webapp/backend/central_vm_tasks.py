import requests

from celery import shared_task
from django.conf import settings

from .models import LambdaInstance, Application


@shared_task(bind=True)
def create_lambda_instance_central_vm(self, auth_token, instance_uuid, instance_name, specs='{}'):
    """
    Makes an HTTP request to Central VM to send information about the new Lambda Instance.
    :param auth_token: The authentication token of the user that owns the Lambda Instance.
    :param instance_uuid: The uuid of the Lambda Instance.
    :param instance_name: The name of the Lambda Instance.
    :param specs: The specifications of the Lambda Instance.
    """

    # Make a POST request to send the information to Central VM. In case of a timeout, retry
    # three(3) times(default Celery retry) and then stop trying.
    try:
        requests.post(
            url=settings.CENTRAL_VM_API + "/lambda_instances/",
            json={
                'uuid': instance_uuid,
                'name': instance_name,
                'instance_info': specs,
                'status': LambdaInstance.PENDING,
                'failure_message': ""
            },
            headers={
                'Authorization': "Token {}".format(auth_token),
                'Content-Type': "application/json"
            })
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        self.retry(countdown=settings.CENTRAL_VM_RETRY_COUNTDOWN)


@shared_task(bind=True)
def set_lambda_instance_status_central_vm(self, auth_token, instance_uuid, status, failure_message):
    """
    Makes an HTTP request to Central VM to change the status of the specified Lambda Instance.
    :param auth_token: The authentication token of the user that owns the Lambda Instance.
    :param instance_uuid: The uuid of the Lambda Instance.
    :param status: The new status state of the Lambda Instance.
    """

    # Make a Post request to send the information to Central VM. In case of a timeout, retry
    # three(3) times(default Celery retry) and then stop trying.
    try:
        requests.post(
            url=(settings.CENTRAL_VM_API + "/lambda_instances/{}/status/").format(instance_uuid),
            json={
                'status': status,
                'failure_message': failure_message
            },
            headers={
                'Authorization': "Token {}".format(auth_token),
                'Content-Type': "application/json"
            })
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        self.retry(countdown=settings.CENTRAL_VM_RETRY_COUNTDOWN)


@shared_task(bind=True)
def delete_lambda_instance_central_vm(self, auth_token, instance_uuid):
    """
    Makes an HTTP request to Central VM to delete the specified Lambda Instance.
    :param auth_token: The authentication token of the user that owns the Lambda Instance.
    :param instance_uuid: The uuid of the Lambda Instance.
    """

    # Make a Delete request to Central VM. In case of a timeout, retry three(3)
    # times(default Celery retry) and then stop trying.
    try:
        requests.delete(
            url=(settings.CENTRAL_VM_API + "/lambda_instances/{}/").format(instance_uuid),
            headers={
                'Authorization': "Token {}".format(auth_token),
                'Content-Type': "application/json"
            })
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        self.retry(countdown=settings.CENTRAL_VM_RETRY_COUNTDOWN)


@shared_task(bind=True)
def create_application_central_vm(self, auth_token, application_uuid, name, description):
    """
    Makes an HTTP request to Central VM to send information about the new Application.
    :param auth_token: The authentication token of the user that owns the Application
    :param application_uuid: The uuid of the Application.
    :param name: The name of the Application.
    :param description: The description of the Application.
    """

    # Make a Post request to send the information to Central VM. In case of a timeout, retry
    # three(3) times(default Celery retry) and then stop trying.
    try:
        requests.post(
            url=settings.CENTRAL_VM_API + "/lambda_applications/",
            json={
                'uuid': "{}".format(application_uuid),
                'name': name,
                'description': description,
                'status': Application.UPLOADING,
                'failure_message': ""
            },
            headers={
                'Authorization': "Token {}".format(auth_token),
                'Content-Type': "application/json"
            })
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        self.retry(countdown=settings.CENTRAL_VM_RETRY_COUNTDOWN)


@shared_task(bind=True)
def set_application_status_central_vm(self, auth_token, application_uuid, status,
                                      failure_message=""):
    """
    Makes an HTTP request to Central VM to update the status of the specified Application.
    :param auth_token: The authentication token of the user that owns the Application.
    :param application_uuid: The uuid of the Application.
    :param status: The new status of the Application.
    :param failure_message: A failure message regarding the status of the Application.
    """

    # Make a Post request to send the information to Central VM. In case of a timeout, retry
    # three(3) times(default Celery retry) and then stop trying.
    try:
        requests.post(
            url=(settings.CENTRAL_VM_API + "/lambda_applications/{}/status/").
            format(application_uuid),
            json={
                'status': status,
                'failure_message': failure_message
            },
            headers={
                'Authorization': "Token {}".format(auth_token),
                'Content-Type': "application/json"
            })
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        self.retry(countdown=settings.CENTRAL_VM_RETRY_COUNTDOWN)


@shared_task(bind=True)
def delete_application_central_vm(self, auth_token, application_uuid):
    """
    Makes an HTTP request to Central VM to delete the specified Application.
    :param auth_token: The authentication token of the user that owns the Application.
    :param application_uuid: The uuid of the Application.
    """

    # Make a Delete request to Central VM. In case of a timeout, retry three(3)
    # times(default Celery retry) and then stop trying.
    try:
        requests.delete(
            url=(settings.CENTRAL_VM_API + "/lambda_applications/{}/").format(application_uuid),
            headers={
                'Authorization': "Token {}".format(auth_token),
                'Content-Type': "application/json"
            })
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        self.retry(countdown=settings.CENTRAL_VM_RETRY_COUNTDOWN)
