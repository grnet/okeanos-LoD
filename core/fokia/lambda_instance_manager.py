import time
from fokia.provisioner import Provisioner
from fokia.ansible_manager import Manager
# import os
# import inspect

# script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
script_path = '/var/www/okeanos-LoD/core/fokia'


def get_cluster_details(cluster_id):
    """
    :param cluster_id: id of the cluster
    :returns: the details of the cluster after retrieving them from the database.
    """
    # TODO
    # 1. create a query for the table cluster requesting the cluster info with this id
    # 2. parse the answer, create a dictionary object with this format:
    """
    {'nodes':[master_id,node1_id,node2_id,...], 'vpn':vpn_id}
    """
    # 3. return dictionary, return null if the query did not return any answer.
    return None


def create_lambda_instance(auth_token=None, master_name='lambda-master',
                           slaves=1, vcpus_master=4, vcpus_slave=4,
                           ram_master=4096, ram_slave=4096, disk_master=40, disk_slave=40,
                           ip_allocation='master', network_request=1,
                           project_name='lambda.grnet.gr'):
    start_time = time.time()

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
                                      project_name=project_name)

    provisioner_response = provisioner.get_cluster_details()
    master_id = provisioner_response['nodes']['master']['id']
    master_ip = provisioner.get_server_private_ip(master_id)
    provisioner_response['nodes']['master']['internal_ip'] = master_ip
    # slave_ids = [slave['id'] for slave in provisioner_response['nodes']['slaves']]
    for i, slave in enumerate(provisioner_response['nodes']['slaves']):
        slave_ip = provisioner.get_server_private_ip(slave['id'])
        provisioner_response['nodes']['slaves'][i]['internal_ip'] = slave_ip
    provisioner_response['pk'] = provisioner.get_private_key()

    print 'response =', provisioner_response
    provisioner_time = time.time()

    ansible_manager = Manager(provisioner_response)
    ansible_manager.create_inventory()

    ansible_result = ansible_manager.run_playbook(
        playbook_file=script_path + "/../../ansible/playbooks/cluster-install.yml")

    ansible_manager.cleanup()

    provisioner_duration = provisioner_time - start_time
    ansible_duration = time.time() - provisioner_time

    print 'VM provisioning took', round(provisioner_duration), 'seconds'
    print 'Ansible playbooks took', round(ansible_duration), 'seconds'
    print 'Ansible result', ansible_result

    return ansible_result


def create_cluster(auth_token=None, master_name='lambda-master',
                   slaves=1, vcpus_master=4, vcpus_slave=4,
                   ram_master=4096, ram_slave=4096, disk_master=40, disk_slave=40,
                   ip_allocation='master', network_request=1, project_name='lambda.grnet.gr'):
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
                                      project_name=project_name)

    provisioner_response = provisioner.get_cluster_details()
    master_id = provisioner_response['nodes']['master']['id']
    master_ip = provisioner.get_server_private_ip(master_id)
    provisioner_response['nodes']['master']['internal_ip'] = master_ip
    # slave_ids = [slave['id'] for slave in provisioner_response['nodes']['slaves']]
    for i, slave in enumerate(provisioner_response['nodes']['slaves']):
        slave_ip = provisioner.get_server_private_ip(slave['id'])
        provisioner_response['nodes']['slaves'][i]['internal_ip'] = slave_ip
    provisioner_response['pk'] = provisioner.get_private_key()

    ansible_manager = Manager(provisioner_response)
    ansible_manager.create_inventory()

    return ansible_manager, provisioner_response


def run_playbook(ansible_manager, playbook):
    ansible_result = ansible_manager.run_playbook(
        playbook_file=script_path + "/../../ansible/playbooks/" + playbook)
    return ansible_result


def destroy_cluster(cloud_name, cluster_id):
    provisioner = Provisioner(cloud_name=cloud_name)
    details = get_cluster_details(cluster_id=cluster_id)
    if details is not None:
        provisioner.delete_lambda_cluster(details)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Okeanos VM provisioning")
    # parser.add_argument('--cloud', type=str, dest="cloud", default="lambda")
    # parser.add_argument('--project-name', type=str, dest="project_name",
    #                     default="lambda.grnet.gr")
    #
    # parser.add_argument('--slaves', type=int, dest='slaves', default=2)
    # parser.add_argument('--vcpus_master', type=int, dest='vcpus_master', default=4)
    # parser.add_argument('--vcpus_slave', type=int, dest='vcpus_slave', default=4)
    # parser.add_argument('--ram_master', type=int, dest='ram_master', default=4096)  # in MB
    # parser.add_argument('--ram_slave', type=int, dest='ram_slave', default=4096)  # in MB
    # parser.add_argument('--disk_master', type=int, dest='disk_master', default=40)  # in GB
    # parser.add_argument('--disk_slave', type=int, dest='disk_slave', default=40)  # in GB
    # parser.add_argument('--ip_allocation', type=str, dest='ip_allocation', default="master",
    #                     help="Choose between none, master, all")
    # parser.add_argument('--network_request', type=int, dest='network_request', default=1)
    # parser.add_argument('--image_name', type=str, dest='image_name', default='debian')
    # parser.add_argument('--action', type=str, dest='action', default='create')
    # parser.add_argument('--cluster_id', type=int, dest='cluster_id', default=0)
    #
    # args = parser.parse_args()

    create_lambda_instance()
