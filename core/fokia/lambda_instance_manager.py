from storm import Storm
from storm.parsers import ssh_config_parser
from fokia.provisioner import Provisioner
from fokia.ansible_manager import Manager
import os
from os.path import join, expanduser, exists
from kamaki.clients import ClientError

check_folders = ['/var/www/okeanos-LoD/ansible', 'okeanos-LoD/ansible', 'ansible', '../ansible',
                 '../../ansible']

ansible_path = os.environ.get('LAMBDA_ANSIBLE_PATH', None)
if not ansible_path:
    for folder in check_folders:
        if exists(folder):
            ansible_path = folder
            break


def create_cluster(cluster_id, auth_token=None, master_name='lambda-master',
                   master_image_id=None, slave_image_id=None,
                   slaves=1, vcpus_master=4, vcpus_slave=4,
                   ram_master=4096, ram_slave=4096, disk_master=40, disk_slave=40,
                   ip_allocation='master', network_request=1, project_name='lambda.grnet.gr',
                   pub_keys=None):
    provisioner = Provisioner(auth_token=auth_token)
    provisioner.create_lambda_cluster(vm_name=master_name,
                                      master_image_id=master_image_id,
                                      slave_image_id=slave_image_id,
                                      slaves=slaves,
                                      vcpus_master=vcpus_master,
                                      vcpus_slave=vcpus_slave,
                                      ram_master=ram_master,
                                      ram_slave=ram_slave,
                                      disk_master=disk_master,
                                      disk_slave=disk_slave,
                                      ip_allocation=ip_allocation,
                                      network_request=network_request,
                                      project_name=project_name,
                                      extra_pub_keys=pub_keys)

    provisioner_response = provisioner.get_cluster_details()

    master_id = provisioner_response['nodes']['master']['id']
    master_ip = provisioner.get_server_private_ip(master_id)
    provisioner_response['nodes']['master']['internal_ip'] = master_ip
    # slave_ids = [slave['id'] for slave in provisioner_response['nodes']['slaves']]
    for i, slave in enumerate(provisioner_response['nodes']['slaves']):
        slave_ip = provisioner.get_server_private_ip(slave['id'])
        provisioner_response['nodes']['slaves'][i]['internal_ip'] = slave_ip
    provisioner_response['pk'] = provisioner.get_private_key()

    __add_private_key(cluster_id, provisioner_response)

    ansible_manager = Manager(provisioner_response)
    ansible_manager.create_inventory()

    return ansible_manager, provisioner_response


def __add_private_key(cluster_id, provisioner_response):
    kf_path = join(expanduser('~/.ssh/lambda_instances/'), str(cluster_id))
    with open(kf_path, 'w') as kf:
        kf.write(provisioner_response['pk'])
    os.chmod(kf_path, 0o600)
    sconfig = ssh_config_parser.ConfigParser(expanduser('~/.ssh/config'))
    sconfig.load()
    master_name = 'snf-' + str(provisioner_response['nodes']['master']['id']) + \
                  '.vm.okeanos.grnet.gr'
    sconfig.add_host(master_name, {
        'IdentityFile': kf_path
    })
    for response in provisioner_response['nodes']['slaves']:
        slave_name = 'snf-' + str(response['id']) + '.local'
        sconfig.add_host(slave_name, {
            'IdentityFile': kf_path,
            'Proxycommand': 'ssh -o StrictHostKeyChecking=no -W %%h:%%p '
                            'root@%s' % (master_name)
        })
    sconfig.write_to_ssh_config()


def __delete_private_key(cluster_id, master_id, slave_ids):
    sconfig = Storm(expanduser('~/.ssh/config'))
    name = 'snf-' + str(master_id) + '.vm.okeanos.grnet.gr'
    sconfig.delete_entry(name)
    for slave_id in slave_ids:
        name = 'snf-' + str(slave_id) + '.local'
        sconfig.delete_entry(name)
    os.remove(join(expanduser('~/.ssh/lambda_instances/'), cluster_id))


def run_playbook(ansible_manager, playbook, only_tags=None, skip_tags=None, extra_vars=None):
    ansible_result = ansible_manager.run_playbook(
        playbook_file=join(ansible_path, "playbooks", playbook),
        only_tags=only_tags, skip_tags=skip_tags, extra_vars=extra_vars)
    return ansible_result


def lambda_instance_destroy(instance_uuid, auth_token,
                            master_id, slave_ids,
                            public_ip_id, private_network_id):
    """
    Destroys the specified lambda instance. The VMs of the lambda instance, along with the public
    ip and the private network used are destroyed and the status of the lambda instance gets
    changed to DESTROYED. There is no going back from this state, the entries are kept to the
    database for reference.
    :param instance_uuid: The uuid of the lambda instance
    :param auth_token: The authentication token of the owner of the lambda instance.
    :param master_id: The ~okeanos id of the VM that acts as the master node.
    :param slave_ids: The ~okeanos ids of the VMs that act as the slave nodes.
    :param public_ip_id: The ~okeanos id of the public ip assigned to master node.
    :param private_network_id: The ~okeanos id of the private network used by the lambda instance.
    """

    provisioner = Provisioner(auth_token=auth_token)

    # Retrieve cyclades compute client
    cyclades_compute_client = provisioner.cyclades

    # Retrieve cyclades network client
    cyclades_network_client = provisioner.network_client

    # Detach the public ip
    port_id = cyclades_network_client.get_floatingip_details(public_ip_id)['port_id']
    if port_id:
        port_status = cyclades_network_client.get_port_details(port_id)['status']
        cyclades_network_client.delete_port(port_id)
        try:
            cyclades_network_client.wait_port_while(port_id, port_status)
        except ClientError as ce:
            if ce.status != 404:
                raise

    # Check if the public ip is attached
    attached_vm = cyclades_network_client.get_floatingip_details(public_ip_id)['instance_id']
    if not attached_vm:
        # Destroy the public ip
        cyclades_network_client.delete_floatingip(public_ip_id)
    else:
        if attached_vm in [master_id] + slave_ids:
            raise ClientError("Destroy failed. Reason: The public IP was not detached")

    # Detach the VMs from the private network
    for server_id in [master_id] + slave_ids:
        ports = [port for port in
                 cyclades_compute_client.get_server_details(server_id)['attachments'] if
                 (int(port['network_id']) == private_network_id)]
        if ports:
            for port in ports:
                port['status'] = cyclades_network_client.get_port_details(port['id'])['status']
                cyclades_network_client.delete_port(port['id'])
                try:
                    cyclades_network_client.wait_port_while(port['id'], port['status'])
                except ClientError as ce:
                    if ce.status != 404:
                        raise

    # Destroy the private network
    cyclades_network_client.delete_network(private_network_id)

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

    # Wait for all VMs to be destroyed
    cyclades_compute_client.wait_server(master_id, current_status=master_status, max_wait=600)
    for i, slave_id in enumerate(slave_ids):
        cyclades_compute_client.wait_server(slave_id, current_status=slaves_status[i], max_wait=600)

    # Delete the private key
    __delete_private_key(instance_uuid, master_id, slave_ids)


if __name__ == "__main__":

    import argparse
    import uuid

    parser = argparse.ArgumentParser(description="Okeanos VM provisioning")
    parser.add_argument('--master-name', type=str, dest="master_name",
                        default="lambda-master",
                        help="Name of Flink master VM [default: lambda-master]")
    parser.add_argument('--slaves', type=int, dest='slaves', default=1,
                        help="Number of Flink slaves [default: 1]")
    parser.add_argument('--vcpus-master', type=int, dest='vcpus_master', default=4,
                        help="Number of CPUs on Flink master [default: 4]")
    parser.add_argument('--vcpus-slave', type=int, dest='vcpus_slave', default=4,
                        help="Number of CPUs on Flink slave(s) [default: 4]")
    parser.add_argument('--ram-master', type=int, dest='ram_master', default=4096,
                        help="Size of RAM on Flink master (in MB) [default: 4096MB]")
    parser.add_argument('--ram-slave', type=int, dest='ram_slave', default=4096,
                        help="Size of RAM on Flink slave(s) (in MB) [default: 4096MB]")
    parser.add_argument('--disk-master', type=int, dest='disk_master', default=40,
                        help="Size of disk on Flink master (in GB) [default: 40GB]")
    parser.add_argument('--disk-slave', type=int, dest='disk_slave', default=40,
                        help="Size of disk on Flink slave(s) (in GB) [default: 40GB]")
    parser.add_argument('--project-name', type=str, dest="project_name",
                        help="~okeanos Project [example: project.grnet.gr]")
    parser.add_argument('--auth-token', type=str, dest="auth_token",
                        help="~okeanos auth token")
    parser.add_argument('--no-images', action='store_false', dest="use_images",
                        default=True, help=argparse.SUPPRESS)
    parser.add_argument('--image-creation', action='store_true', dest="image_creation",
                        default=False, help=argparse.SUPPRESS)

    args = parser.parse_args()

    keys_folder = expanduser('~/.ssh/lambda_instances/')
    if not os.path.exists(keys_folder):
        choice = raw_input("{} was not found. "
                           "Do you want to have it created for you?"
                           " (Y/n)?".format(keys_folder))
        if choice.lower() in ["", "y", "yes"]:
            os.mkdir(keys_folder, 0o755)

    use_images = args.use_images
    image_creation = args.image_creation

    if use_images and not image_creation:
        master_image_id = 'ef4d0aec-896a-4df1-80f5-b7c31b475499'
        slave_image_id = '3ac53ab3-4d3c-4fb9-8816-525bdd9ab975'
    else:
        master_image_id = None
        slave_image_id = None
    ansible_manager, provisioner_response = create_cluster(cluster_id=uuid.uuid4(),
                                                           auth_token=args.auth_token,
                                                           master_image_id=master_image_id,
                                                           slave_image_id=slave_image_id,
                                                           master_name=args.master_name,
                                                           slaves=args.slaves,
                                                           vcpus_master=args.vcpus_master,
                                                           vcpus_slave=args.vcpus_slave,
                                                           ram_master=args.ram_master,
                                                           ram_slave=args.ram_slave,
                                                           disk_master=args.disk_master,
                                                           disk_slave=args.disk_slave,
                                                           project_name=args.project_name)

    if not image_creation:
        # Create lambda instance
        only_tags = None
        if use_images:
            only_tags = ['common-configure']
        run_playbook(ansible_manager, 'initialize.yml', only_tags=only_tags)
        if use_images:
            only_tags = ['common-configure', 'image-configure']
        run_playbook(ansible_manager, 'common-install.yml', only_tags=only_tags)
        if use_images:
            only_tags = ['image-configure']
        run_playbook(ansible_manager, 'hadoop-install.yml', only_tags=only_tags)
        run_playbook(ansible_manager, 'kafka-install.yml', only_tags=only_tags)
        run_playbook(ansible_manager, 'flink-install.yml', only_tags=only_tags)
        run_playbook(ansible_manager, 'flume-install.yml', only_tags=only_tags)

    else:
        # Used for image creation, does not configure or start lambda instance
        skip_tags = ['image-configure']
        run_playbook(ansible_manager, 'initialize.yml')
        run_playbook(ansible_manager, 'common-install.yml', skip_tags=skip_tags)
        run_playbook(ansible_manager, 'hadoop-install.yml', skip_tags=skip_tags)
        run_playbook(ansible_manager, 'kafka-install.yml', skip_tags=skip_tags)
        run_playbook(ansible_manager, 'flink-install.yml', skip_tags=skip_tags)
        run_playbook(ansible_manager, 'flume-install.yml', skip_tags=skip_tags)
