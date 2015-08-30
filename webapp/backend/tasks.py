from celery import shared_task

from kamaki.clients import ClientError
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
            if cyclades.get_server_details(slave_id)["status"] != "ACTIVE":
                cyclades.start_server(slave_id)

        # Wait until all slave nodes have been started.
        for slave_id in slave_ids:
            cyclades.wait_server(slave_id, current_status="STOPPED")

        # Start master node.
        if cyclades.get_server_details(master_id)["status"] != "ACTIVE":
            cyclades.start_server(master_id)

        # Wait until master node has been started.
        cyclades.wait_server(master_id, current_status="STOPPED")

        # Update lambda instance status on the database to started.
        set_lambda_instance_status.delay(instance_uuid, LambdaInstance.STARTED)
    except ClientError as exception:
        set_lambda_instance_status.delay(instance_uuid, LambdaInstance.FAILED, exception.message)


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
        if cyclades.get_server_details(master_id)["status"] != "STOPPED":
            cyclades.shutdown_server(master_id)

        # Wait until master node has been stopped.
        cyclades.wait_server(master_id, current_status="ACTIVE")

        # Stop all slave nodes.
        for slave_id in slave_ids:
            if cyclades.get_server_details(slave_id)["status"] != "STOPPED":
                cyclades.shutdown_server(slave_id)

        # Wait until all slave nodes have been stopeed.
        for slave_id in slave_ids:
            cyclades.wait_server(slave_id, current_status="ACTIVE")

        # Update lambda instance status on the database to started.
        set_lambda_instance_status.delay(instance_uuid, LambdaInstance.STOPPED)
    except ClientError as exception:
        set_lambda_instance_status.delay(instance_uuid, LambdaInstance.FAILED, exception.message)
