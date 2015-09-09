import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from kamaki.clients.utils import https
from kamaki.clients import ClientError
from kamaki import defaults
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.cyclades import CycladesComputeClient, CycladesNetworkClient


def patch_certs(cert_path=None):
    """
    Patch http certificates or ignore_ssl() if no certificates ca be found
    :param cert_path: Path to the certificate file
    """

    if not defaults.CACERTS_DEFAULT_PATH:
        if cert_path:
            https.patch_with_certs(cert_path)
        else:
            try:
                from ssl import get_default_verify_paths
                cert_path = get_default_verify_paths().cafile or \
                    get_default_verify_paths().openssl_cafile
            except:
                pass

            if cert_path:
                https.patch_with_certs(cert_path)
            else:
                logger.warn("COULD NOT FIND ANY CERTIFICATES, PLEASE SET THEM IN YOUR "
                            ".kamakirc global section, option ca_certs")
                https.patch_ignore_ssl()


def check_auth_token(auth_token, auth_url=None):
    """
    Checks the validity of a user authentication token.

    :param auth_token: User authentication token
    :param auth_url: Authentication url
    :return: tuple(Success status, details)
    """

    if not auth_url:
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"
    patch_certs()
    cl = AstakosClient(auth_url, auth_token)
    try:
        user_info = cl.authenticate()
    except ClientError as ex:
        if ex.message == 'UNAUTHORIZED':
            return False, ex.details
        else:
            raise
    return True, user_info


def lambda_instance_start(auth_url, auth_token, master_id, slave_ids):
    """
    Starts the VMs of a lambda instance using kamaki. Starting the master node will cause the lambda
    services to start. That is why all slave nodes must be started before starting the master node.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the owner of the lambda instance.
    :param master_id: The ~okeanos id of the VM that acts as the master node.
    :param slave_ids: The ~okeanos ids of the VMs that act as the slave nodes.
    """

    # Create cyclades compute client.
    cyclades_compute_url = AstakosClient(auth_url, auth_token).get_endpoint_url(
        CycladesComputeClient.service_type)
    cyclades_compute_client = CycladesComputeClient(cyclades_compute_url, auth_token)

    # Start all slave nodes.
    for slave_id in slave_ids:
        if cyclades_compute_client.get_server_details(slave_id)["status"] != "ACTIVE":
            cyclades_compute_client.start_server(slave_id)

    # Wait until all slave nodes have been started.
    for slave_id in slave_ids:
        cyclades_compute_client.wait_server(slave_id, current_status="STOPPED")

    # Start master node.
    if cyclades_compute_client.get_server_details(master_id)["status"] != "ACTIVE":
        cyclades_compute_client.start_server(master_id)

    # Wait until master node has been started.
    cyclades_compute_client.wait_server(master_id, current_status="STOPPED")


def lambda_instance_stop(auth_url, auth_token, master_id, slave_ids):
    """
    Stops the VMs of a lambda instance using kamaki. Stopping the master node will cause the lambda
    services to stop. That is why the master node must be stopped before stopping any of the slave
    nodes.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the owner of the lambda instance.
    :param master_id: The ~okeanos id of the VM that acts as the master node.
    :param slave_ids: The ~okeanos ids of the VMs that act as the slave nodes.
    """

    # Create cyclades client.
    cyclades_compute_url = AstakosClient(auth_url, auth_token).get_endpoint_url(
        CycladesComputeClient.service_type)
    cyclades_compute_client = CycladesComputeClient(cyclades_compute_url, auth_token)

    # Stop master node.
    if cyclades_compute_client.get_server_details(master_id)["status"] != "STOPPED":
        cyclades_compute_client.shutdown_server(master_id)

    # Wait until master node has been stopped.
    cyclades_compute_client.wait_server(master_id, current_status="ACTIVE")

    # Stop all slave nodes.
    for slave_id in slave_ids:
        if cyclades_compute_client.get_server_details(slave_id)["status"] != "STOPPED":
            cyclades_compute_client.shutdown_server(slave_id)

    # Wait until all slave nodes have been stopped.
    for slave_id in slave_ids:
        cyclades_compute_client.wait_server(slave_id, current_status="ACTIVE")


def lambda_instance_destroy(auth_url, auth_token, master_id, slave_ids, public_ip_id,
                            private_network_id):
    """
    Destroys the specified lambda instance. The VMs of the lambda instance, along with the public
    ip and the private network used are destroyed and the status of the lambda instance gets
    changed to DESTROYED. There is no going back from this state, the entries are kept to the
    database for reference.
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
