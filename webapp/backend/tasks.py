from celery import shared_task

from kamaki.clients.astakos import AstakosClient
from kamaki.clients.cyclades import CycladesComputeClient

from .events import set_lambda_instance_status
from .models import LambdaInstance

@shared_task
def lambda_instance_start(instance_uuid, auth_url, auth_token, master_id, slave_ids):
    """
    Starts the VMs of a lambda instance using kamaki. Starting the master node will cause the lambda
    services to start. That is why all slave nodes must be started before starting the master node.
    token: The token of the owner of the lambda instance. The validity check of the token should
           have already been done.
    uuid: The uuid of the lambda instance.
    """

    cyclades_url = AstakosClient(auth_url, auth_token).get_endpoint_url(
                   CycladesComputeClient.service_type)
    cyclades = CycladesComputeClient(cyclades_url, auth_token)

    try:
        # Start all slave nodes.
        for slave_id in slave_ids:
            cyclades.start_server(slave_id)

        # Start master node.
        cyclades.start_server(master_id)

        # Update lambda instance status on the database to started.
        set_lambda_instance_status(instance_uuid, LambdaInstance.STARTED).delay()
    except:
        set_lambda_instance_status(instance_uuid, LambdaInstance.FAILED).delay()
        return


@shared_task
def lambda_instance_stop(instance_uuid, auth_url, auth_token, master_id, slave_ids):
    """
    Stops the VMs of a lambda instance using kamaki. Stopping the master node will cause the lambda
    services to stop. That is why the master node must be stopped before stopping any of the slave
    nodes.
    token: The token of the owner of the lambda instance. The validity check of the token should
           have already been done.
    uuid: The uuid of the lambda instance.
    """

    cyclades_url = AstakosClient(auth_url, auth_token).get_endpoint_url(
                   CycladesComputeClient.service_type)
    cyclades = CycladesComputeClient(cyclades_url, auth_token)

    try:
        # Stop master node.
        cyclades.shutdown_server(master_id)

        # Stop all slave nodes.
        for slave_id in slave_ids:
            cyclades.shutdown_server(slave_id)

        # Update lambda instance status on the database to started.
        set_lambda_instance_status(instance_uuid, LambdaInstance.STOPPED).delay()
    except:
        set_lambda_instance_status(instance_uuid, LambdaInstance.FAILED).delay()