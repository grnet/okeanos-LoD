from celery import shared_task

from kamaki.clients import astakos, cyclades

@shared_task
def lambda_instance_start(auth_token, uuid):
    """
    Starts the VMs of a lambda instance using kamaki. Starting the master node will cause the lambda
    services to start. That is why all slave nodes must be started before starting the master node.
    token: The token of the owner of the lambda instance. The validity check of the token should
           have already been done.
    uuid: The uuid of the lambda instance.
    """

    compute_url = astakos.get_endpoint_url(
                  cyclades.CycladesComputeClient.service_type)
    cycladesClient = cyclades.CycladesComputeClient(compute_url, auth_token)

    # Start all slave nodes.

    # Start master node.


@shared_task
def lambda_instance_stop(auth_token, uuid):
    """
    Stops the VMs of a lambda instance using kamaki. Stopping the master node will cause the lambda
    services to stop. That is why the master node must be stopped before stopping any of the slave
    nodes.
    token: The token of the owner of the lambda instance. The validity check of the token should
           have already been done.
    uuid: The uuid of the lambda instance.
    """

    compute_url = astakos.get_endpoint_url(
                  cyclades.CycladesComputeClient.service_type)
    cycladesClient = cyclades.CycladesComputeClient(compute_url, auth_token)

    # Stop master node.

    # Stop all slave nodes.
