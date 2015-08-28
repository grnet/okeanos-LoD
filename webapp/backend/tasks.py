from celery import shared_task


@shared_task
def lambda_instance_start(token, uuid):
  """
  Starts the VMs of a lambda instance using kamaki.
  token: The token of the owner of the lambda instance. The validity check of the token should
         have already been done.
  uuid: The uuid of the lambda instance.
  """


@shared_task
def lambda_instance_stop(token, uuid):
  """
  Stops the VMs of a lambda instance using kamaki.
  token: The token of the owner of the lambda instance. The validity check of the token should
         have already been done.
  uuid: The uuid of the lambda instance.
  """
