from celery import shared_task

from kamaki.clients import ClientError
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.cyclades import CycladesComputeClient, CycladesNetworkClient

from .events import set_lambda_instance_status
from .models import LambdaInstance


@shared_task
def lambda_instance_start(instance_uuid, auth_url, auth_token, master_id, slave_ids):
    """
    Starts the VMs of a lambda instance using kamaki. Starting the master node will cause the lambda
    services to start. That is why all slave nodes must be started before starting the master node.
    :param instance_uuid: The uuid of the lambda instance.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the owner of the lambda instance.
    :param master_id: The ~okeanos id of the VM that acts as the master node.
    :param slave_ids: The ~okeanos ids of the VMs that act as the slave nodes.
    """

    # Create cyclades client.
    cyclades_compute_url = AstakosClient(auth_url, auth_token).get_endpoint_url(
        CycladesComputeClient.service_type)
    cyclades = CycladesComputeClient(cyclades_compute_url, auth_token)

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
    :param instance_uuid: The uuid of the lambda instance.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the owner of the lambda instance.
    :param master_id: The ~okeanos id of the VM that acts as the master node.
    :param slave_ids: The ~okeanos ids of the VMs that act as the slave nodes.
    """

    # Create cyclades client.
    cyclades_compute_url = AstakosClient(auth_url, auth_token).get_endpoint_url(
        CycladesComputeClient.service_type)
    cyclades = CycladesComputeClient(cyclades_compute_url, auth_token)

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


@shared_task
def lambda_instance_destroy(instance_uuid, auth_url, auth_token, master_id, slave_ids,
                            public_ip_id, private_network_id):
    """
    Destroys the specified lambda instance. The VMs of the lambda instance, along with the public
    ip and the private network used are destroyed and the status of the lambda instance gets
    changed to DESTROYED. There is no going back from this state, the entries are kept to the
    database for reference.
    :param instance_uuid: The uuid of the lambda instance.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the owner of the lambda instance.
    :param master_id: The ~okeanos id of the VM that acts as the master node.
    :param slave_ids: The ~okeanos ids of the VMs that act as the slave nodes.
    :param public_ip_id: The ~okeanos id of the public ip assigned to master node.
    :param private_network_id: The ~okeanos id of the private network used by the lambda instance.
    """

    # Create cyclades compute client.
    cyclades_compute_url = AstakosClient(auth_url, auth_token).get_endpoint_url(
        CycladesComputeClient.service_type)
    cyclades_compute_client = CycladesComputeClient(cyclades_compute_url, auth_token)

    # Create cyclades network client.
    cyclades_network_url = AstakosClient(auth_url, auth_token).get_endpoint_url(
        CycladesNetworkClient.service_type)
    cyclades_network_client = CycladesNetworkClient(cyclades_network_url, auth_token)

    try:
        # Get the current status of the VMs.
        master_status = cyclades_compute_client.get_server_details(master_id)["status"]
        slaves_status = []
        for slave_id in slave_ids:
            slaves_status.append(cyclades_compute_client.get_server_details(slave_id)["status"])

        # Destroy all the VMs without caring for properly stopping the lambda services.
        # Destroy master node.
        if cyclades_compute_client.get_server_details(master_id)["status"] != "DELETED":
            cyclades_compute_client.delete_server(master_id)

        # Destroy all slave nodes.
        for slave_id in slave_ids:
            if cyclades_compute_client.get_server_details(slave_id)["status"] != "DELETED":
                cyclades_compute_client.delete_server(slave_id)

        # Wait for all the VMs to be destroyed before destroyed the public ip and the
        # private network.
        cyclades_compute_client.wait_server(master_id, current_status=master_status)
        for i, slave_id in enumerate(slave_ids):
            cyclades_compute_client.wait_server(slave_id, current_status=slaves_status[i])

        # Destroy the public ip.
        cyclades_network_client.delete_floatingip(public_ip_id)

        # Destroy the private network.
        cyclades_network_client.delete_network(private_network_id)

        # Update lambda instance status on the database to destroyed.
        set_lambda_instance_status.delay(instance_uuid, LambdaInstance.DESTROYED)
    except ClientError as exception:
        set_lambda_instance_status.delay(instance_uuid, LambdaInstance.FAILED, exception.message)
