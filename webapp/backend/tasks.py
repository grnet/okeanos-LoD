from celery import shared_task

from kamaki.clients import ClientError

import fokia.utils

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

    try:
        # Start the VMs of the specified lambda instance.
        fokia.lambda_instance_start(auth_url, auth_token, master_id, slave_ids)

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

    try:
        # Stop the VMs of the specified lambda instance.
        fokia.lambda_instance_stop(auth_url, auth_token, master_id, slave_ids)

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

    try:
        # Destroy all VMs, the public ip and the private network of the lambda instance.
        fokia.lambda_instance_destroy(auth_url, auth_token, master_id, slave_ids, public_ip_id,
                                      private_network_id)

        # Update lambda instance status on the database to destroyed.
        set_lambda_instance_status.delay(instance_uuid, LambdaInstance.DESTROYED)
    except ClientError as exception:
        set_lambda_instance_status.delay(instance_uuid, LambdaInstance.FAILED, exception.message)
