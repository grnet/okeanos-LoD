from celery import shared_task

from .models import LambdaInstance


@shared_task
def set_lambda_instance_status(uuid, status, failure_message=""):
    """
    Sets the status of a specified lambda instance to the specified status.
    The existence of the lambda instance should have been previously checked.
    instance_uuid: The uuid of the lambda instance.
    status: The integer that specifies the new status of the specified lambda instance.
            For more information see models.py.
    """

    lambda_instance = LambdaInstance.objects.get(uuid=uuid)
    lambda_instance.status = status
    lambda_instance.failure_message = failure_message
    lambda_instance.save()


@shared_task
def create_new_lambda_instance(instance_uuid, instance_name, specs='{}'):
    """
    Creates a new lambda instance entry into the DataBase
    A unique uuid that identifies the lambda instance is created,
    after checking that it does not belong to another lambda instance.
    The instance info is inserted in json format, the instance name is
    specified as argument, and the status is set to 'PENDING' (default)
    """

    instance = LambdaInstance.objects.create(
        uuid=instance_uuid, name=instance_name, instance_info=specs, status='PENDING')
    instance.save()
