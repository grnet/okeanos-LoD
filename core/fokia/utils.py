import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os

from kamaki.clients.utils import https
from kamaki.clients import ClientError
from kamaki import defaults
from kamaki.clients.pithos import PithosClient
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.cyclades import CycladesComputeClient
from kamaki.cli.config import Config as KamakiConfig

try_paths = ['/etc/ssl/certs/ca-certificates.crt', '/usr/local/etc/openssl/cert.pem']


def patch_certs():
    """
    Patch http certificates or ignore_ssl() if no certificates ca be found
    :param cert_path: Path to the certificate file
    """

    if defaults.CACERTS_DEFAULT_PATH and os.path.exists(defaults.CACERTS_DEFAULT_PATH):
        return

    try:
        config = KamakiConfig()
        cert_path = config.get('global', 'ca_certs')
    except:
        cert_path = None
    if cert_path and os.path.exists(cert_path):
        https.patch_with_certs(cert_path)
        return

    try:
        from ssl import get_default_verify_paths
        cert_path = get_default_verify_paths().cafile or \
            get_default_verify_paths().openssl_cafile
    except:
        pass
    if cert_path and os.path.exists(cert_path):
        https.patch_with_certs(cert_path)
        return

    for path in try_paths:
        if os.path.exists(path):
            https.patch_with_certs(path)
            return

    logger.warn("COULD NOT FIND ANY CERTIFICATES, PLEASE SET THEM IN YOUR "
                ".kamakirc 'global' SECTION, OPTION 'ca_certs'")
    https.patch_ignore_ssl()
    return


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
        cyclades_compute_client.wait_server(slave_id, current_status="STOPPED", max_wait=600)

    # Start master node.
    if cyclades_compute_client.get_server_details(master_id)["status"] != "ACTIVE":
        cyclades_compute_client.start_server(master_id)

    # Wait until master node has been started.
    cyclades_compute_client.wait_server(master_id, current_status="STOPPED", max_wait=600)


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
    cyclades_compute_client.wait_server(master_id, current_status="ACTIVE", max_wait=600)

    # Stop all slave nodes.
    for slave_id in slave_ids:
        if cyclades_compute_client.get_server_details(slave_id)["status"] != "STOPPED":
            cyclades_compute_client.shutdown_server(slave_id)

    # Wait until all slave nodes have been stopped.
    for slave_id in slave_ids:
        cyclades_compute_client.wait_server(slave_id, current_status="ACTIVE", max_wait=600)


def upload_file_to_pithos(auth_url, auth_token, container_name, project_name, local_file):
    """
    Uploads a given file to a specified container, under a specified name on Pithos.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the user.
    :param container_name: The name of the Pithos container to be used.
    :param file_descriptor: A file descriptor of the file saved of the local file system.
    """

    # Create Astakos client.
    astakos_client = AstakosClient(auth_url, auth_token)

    # Create Pithos client.
    pithos_url = astakos_client.get_endpoint_url(PithosClient.service_type)
    pithos_client = PithosClient(pithos_url, auth_token)
    pithos_client.account = astakos_client.user_info['id']

    # Get the project id.
    if project_name != "":
        project_id = astakos_client.get_projects(**{'name': project_name})[0]['id']
    else:
        project_id = astakos_client.get_projects()[0]['id']

    # Choose the container on Pithos that is used to store application. If the container doesn't
    # exist, create it.
    containers = pithos_client.list_containers()
    if not any(container['name'] == container_name for container in containers):
        pithos_client.create_container(container_name, project_id=project_id)
    pithos_client.container = container_name

    # Upload file to Pithos.
    pithos_client.upload_object(os.path.basename(local_file.name), local_file)


def delete_file_from_pithos(auth_url, auth_token, container_name, filename):
    """
    Deletes a file from a specified container on Pithos.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the user.
    :param container_name: The name of the Pithos container to be used.
    :param filename: The name of the file to be deleted.
    """

    # Create Astakos client.
    astakos_client = AstakosClient(auth_url, auth_token)

    # Create Pithos client.
    pithos_url = astakos_client.get_endpoint_url(PithosClient.service_type)
    pithos_client = PithosClient(pithos_url, auth_token)
    pithos_client.account = astakos_client.user_info['id']
    pithos_client.container = container_name

    # Delete the file from Pithos.
    pithos_client.delete_object(filename)


def download_file_from_pithos(auth_url, auth_token, container_name, filename, destination):
    """
    Downloads a specified file from Pithos.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the user.
    :param container_name: The name of the Pithos container to be used.
    :param filename: The name of the file to be downloaded.
    :param destination: The place where the downloaded file will be saved.
    """

    # Create Astakos client.
    astakos_client = AstakosClient(auth_url, auth_token)

    # Create Pithos client.
    pithos_url = astakos_client.get_endpoint_url(PithosClient.service_type)
    pithos_client = PithosClient(pithos_url, auth_token)
    pithos_client.account = astakos_client.user_info['id']
    pithos_client.container = container_name

    # Download the file from Pithos.
    pithos_client.download_object(filename, destination)


def get_user_okeanos_projects(auth_url, auth_token):
    """
    Fetches the ~okeanos projects on which the user is a member, and returns their names and ids.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the user.
    :return: Returns a list with the requested projects. Each object of the list is a dictionary
             with field 'id' and 'name'.
    """

    # Create astakos client.
    astakos_client = AstakosClient(auth_url, auth_token)

    # Get the names and the ids of user's projects.
    okeanos_projects = list()

    for okeanos_project in astakos_client.get_projects():
        okeanos_projects.append({'id': okeanos_project['id'], 'name': okeanos_project['name']})

    return okeanos_projects


def get_vm_parameter_values(auth_url, auth_token):
    """
    Fetches from ~okeanos the available values for the number of CPUs, the amount of RAM and the
    size of the Disk on a single VM.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the user.
    :return: Returns a dictionary with keys 'vcpus', 'ram' and 'disk'. Each value is a list with
             the corresponding available values.
    """

    # Create cyclades compute client.
    cyclades_url = AstakosClient(auth_url, auth_token).\
        get_endpoint_url(CycladesComputeClient.service_type)
    cyclades_compute_client = CycladesComputeClient(cyclades_url, auth_token)

    # Get all the flavors from ~okeanos and keep only those which are allowed to be created.
    flavors = cyclades_compute_client.list_flavors(detail=True)

    allowed_flavors = list()
    for flavor in flavors:
        if flavor['SNF:allow_create']:
            allowed_flavors.append(flavor)

    # Get the values of the parameters found inside the allowed flavors.
    vm_parameter_values = {'vcpus': set(), 'ram': set(), 'disk': set()}
    for allowed_flavor in allowed_flavors:
        for parameter, values in vm_parameter_values.iteritems():
            values.add(allowed_flavor[parameter])

    # Change the sets to lists in each parameter's values.
    for parameter in vm_parameter_values.iterkeys():
        vm_parameter_values[parameter] = list(vm_parameter_values[parameter])
        vm_parameter_values[parameter].sort()

    return vm_parameter_values
