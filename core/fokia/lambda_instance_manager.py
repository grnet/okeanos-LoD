from storm import Storm
from storm.parsers import ssh_config_parser
from fokia.provisioner import Provisioner
from fokia.ansible_manager import Manager
import os
from os.path import join, expanduser, exists

check_folders = ['/var/www/okeanos-LoD/ansible', 'okeanos-LoD/ansible', 'ansible', '../ansible',
                 '../../ansible']

ansible_path = os.environ.get('LAMBDA_ANSIBLE_PATH', None)
if not ansible_path:
    for folder in check_folders:
        if exists(folder):
            ansible_path = folder
            break


def create_cluster(cluster_id, auth_token=None, master_name='lambda-master',
                   slaves=1, vcpus_master=4, vcpus_slave=4,
                   ram_master=4096, ram_slave=4096, disk_master=40, disk_slave=40,
                   ip_allocation='master', network_request=1, project_name='lambda.grnet.gr',
                   pub_keys=None):
    provisioner = Provisioner(auth_token=auth_token)
    provisioner.create_lambda_cluster(vm_name=master_name,
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


def run_playbook(ansible_manager, playbook, tags=None, extra_vars=None):
    ansible_result = ansible_manager.run_playbook(
        playbook_file=join(ansible_path, "playbooks", playbook), tags=tags, extra_vars=extra_vars)
    return ansible_result


def lambda_instance_destroy(instance_uuid, auth_token,
                            master_id, slave_ids,
                            public_ip_id, private_network_id):
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

    provisioner = Provisioner(auth_token=auth_token)

    # Retrieve cyclades compute client
    cyclades_compute_client = provisioner.cyclades

    # Retrieve cyclades network client
    cyclades_network_client = provisioner.network_client

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
    cyclades_compute_client.wait_server(master_id, current_status=master_status, max_wait=600)
    for i, slave_id in enumerate(slave_ids):
        cyclades_compute_client.wait_server(slave_id, current_status=slaves_status[i], max_wait=600)

    # Destroy the public ip.
    cyclades_network_client.delete_floatingip(public_ip_id)

    # Destroy the private network.
    cyclades_network_client.delete_network(private_network_id)

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
    parser.add_argument('--vcpus_master', type=int, dest='vcpus_master', default=4,
                        help="Number of CPUs on Flink master [default: 4]")
    parser.add_argument('--vcpus_slave', type=int, dest='vcpus_slave', default=4,
                        help="Number of CPUs on Flink slave(s) [default: 4]")
    parser.add_argument('--ram_master', type=int, dest='ram_master', default=4096,
                        help="Size of RAM on Flink master (in MB) [default: 4096MB]")
    parser.add_argument('--ram_slave', type=int, dest='ram_slave', default=4096,
                        help="Size of RAM on Flink slave(s) (in MB) [default: 4096MB]")
    parser.add_argument('--disk_master', type=int, dest='disk_master', default=40,
                        help="Size of disk on Flink master (in GB) [default: 40GB]")
    parser.add_argument('--disk_slave', type=int, dest='disk_slave', default=40,
                        help="Size of disk on Flink slave(s) (in GB) [default: 40GB]")
    parser.add_argument('--project-name', type=str, dest="project_name",
                        default="project.grnet.gr",
                        help="~okeanos Project [default: project.grnet.gr]")

    args = parser.parse_args()

    keys_folder = expanduser('~/.ssh/lambda_instances/')
    if not os.path.exists(keys_folder):
        choice = raw_input("{} was not found. "
                           "Do you want to have it created for you?"
                           " (Y/n)?".format(keys_folder))
        if choice.lower() in ["", "y", "yes"]:
            os.mkdir(keys_folder, 0o755)

    ansible_manager, provisioner_response = create_cluster(cluster_id=uuid.uuid4(),
                                                           master_name=args.master_name,
                                                           slaves=args.slaves,
                                                           vcpus_master=args.vcpus_master,
                                                           vcpus_slave=args.vcpus_slave,
                                                           ram_master=args.ram_master,
                                                           ram_slave=args.ram_slave,
                                                           disk_master=args.disk_master,
                                                           project_name=args.project_name)
    run_playbook(ansible_manager, 'initialize.yml')
    run_playbook(ansible_manager, 'common-install.yml')
    run_playbook(ansible_manager, 'hadoop-install.yml')
    run_playbook(ansible_manager, 'kafka-install.yml')
    run_playbook(ansible_manager, 'flink-install.yml')
