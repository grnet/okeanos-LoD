from celery import shared_task
from .models import LambdaInstance, LambdaApplication

@shared_task
def createLambdaInstance(uuid, instance_name, instance_info,
                         owner, status, failure_message=""):
    LambdaInstance.objects.create(
        uuid=uuid, name=instance_name, instance_info=instance_info, owner=owner,
        status=status, failure_message=failure_message
    )

@shared_task
def updateLambdaInstanceStatus(uuid, status, failure_message):
    """

    :param uuid: The Unique identifier of the lambda instance to be updated
    :param status: The status value to persist in the database.
    :param failure_message:  The relevant to the status message to persist in the database.
    :return:
    """

    lambda_instance = LambdaInstance.objects.get(uuid=uuid)
    lambda_instance.status = status
    if failure_message:
        lambda_instance.failure_message = failure_message
    lambda_instance.save()

@shared_task
def deleteLambdaInstance(uuid):
    """

    :param uuid: The Unique identifier of the lambda cluster to be deleted.
    :return:
    """
    lambda_instance = LambdaInstance.objects.get(uuid=uuid)
    lambda_instance.delete()

@shared_task
def createLambdaApplication(uuid, status, name="", description="",
                            owner=None, failure_message=""):
    """
    Create a new lambda application entry.
    :param uuid: The Unique identifier of the application to be created.
    :param status: The status of the lambda application.
    :param name: The name of the lambda application.
    :param description: The description of the lambda application
    :param owner: The owner of the lambda appplication. Should be the same with
    the lambda instance running the application.
    :param failure_message: The failure message of the application, if applicable.
    :return:
    """
    LambdaApplication.objects.create(uuid=uuid, name=name, description=
                                     description, owner=owner,
                                     status=status, failure_message=
                                     failure_message)


@shared_task
def updateLambdaApplicationStatus(uuid, status, failure_message):
    """
    Update the status and failure message of a lambda application.
    :param uuid: The Unique identifier of the application to be updated.
    :param status: The application's new status value.
    :param failure_message: The failure message of the application, if applicable.
    :return:
    """
    lambda_application = LambdaApplication.objects.get(uuid=uuid)
    lambda_application.status = status
    if failure_message:
        lambda_application.failure_message = failure_message
    lambda_application.save()



@shared_task
def deleteLambdaApplication(uuid):
    """
    Delete an existent lambda application.
    :param uuid: The Unique identifier of the lambda application to be deleted.
    :return:
    """
    lambda_application = LambdaApplication.objects.get(uuid=uuid)
    lambda_application.delete()

