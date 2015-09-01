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
