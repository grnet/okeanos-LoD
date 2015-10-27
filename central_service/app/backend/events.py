from celery import shared_task
from .models import LambdaInstance, LambdaApplication


@shared_task
def createLambdaInstance(uuid, instance_name, instance_info,
                         owner, status, failure_message=""):
    """
    Celery task responsible for creating a new Lambda Instance in the database.
    :param uuid: The Unique Identifier of the Lambda Instance.
    :param instance_name: Tha Lambda Instance's name.
    :param instance_info: Json with the specifications of the Lambda Instance.
    :param owner: The actual owner of the Lambda Instance to be created.
    :param status: The status of the Lambda Instance.
    :param failure_message: The failure message of the lambda Instance.
    """
    LambdaInstance.objects.create(
        uuid=uuid, name=instance_name, instance_info=instance_info, owner=owner,
        status=status, failure_message=failure_message
    )


@shared_task
def updateLambdaInstanceStatus(uuid, status, failure_message):
    """
    Celery task responsible for updating the status of a specific Lambda Instance in the database.
    :param uuid: The Unique identifier of the Lambda Instance to be updated
    :param status: The status value to persist in the database.
    :param failure_message:  The relevant to the status message to persist in the database.
    """

    lambda_instance = LambdaInstance.objects.get(uuid=uuid)
    lambda_instance.status = status
    if failure_message:
        lambda_instance.failure_message = failure_message
    lambda_instance.save()


@shared_task
def deleteLambdaInstance(uuid):
    """
    Celery task responsible for deleting the specified by uuid Lambda Instance from the database.
    :param uuid: The Unique identifier of the Lambda Instance to be deleted.
    """
    lambda_instance = LambdaInstance.objects.get(uuid=uuid)
    lambda_instance.status = '6'
    lambda_instance.save()


@shared_task
def createLambdaApplication(uuid, status, name="", description="",
                            owner=None, failure_message=""):
    """
    Celery task responsible for creating a new Lambda Application in the database.
    :param uuid: The Unique identifier of the Lambda Application to be created.
    :param status: The Status of the Lambda Application.
    :param name: The name of the Lambda Application.
    :param description: The description of the Lambda Application
    :param owner: The owner of the lambda appplication. Should be the same with
    the lambda instance running the application.
    :param failure_message: The failure message of the application, if applicable.
    """
    LambdaApplication.objects.create(uuid=uuid, name=name, description=description,
                                     owner=owner, status=status,
                                     failure_message=failure_message)


@shared_task
def updateLambdaApplicationStatus(uuid, status, failure_message):
    """
    Celery task responsible for updating the status of a specific
    Lambda Application in the database.
    :param uuid: The Unique identifier of the Lambda Application to be updated.
    :param status: The Lambda Application's new status value.
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
    Celery task responsible for deleting the specified by uuid Lambda Application from the database.
    :param uuid: The Unique identifier of the Lambda Application to be deleted.
    :return:
    """
    lambda_application = LambdaApplication.objects.get(uuid=uuid)
    lambda_application.delete()
