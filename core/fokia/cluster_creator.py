import argparse
import time
import os
import inspect
from fokia.provisioner import Provisioner
from fokia.ansible_manager import Manager

def get_cluster_details(cluster_id):
    """
    :param cluster_id: id of the cluster
    :returns: the details of the cluster after retrieving them from the database.
    """
    #TODO
    #1. create a query for the table cluster requesting the cluster info with this id
    #2. parse the answer, create a dictionary object with this format:
    """
    {'nodes':[master_id,node1_id,node2_id,...], 'vpn':vpn_id}
    """
    #3. return dictionary, return null if the query did not return any answer.


if __name__ == "__main__":
    start_time = time.time()
    script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    parser = argparse.ArgumentParser(description="Okeanos VM provisioning")
    parser.add_argument('--cloud', type=str, dest="cloud", default="lambda")
    parser.add_argument('--project-name', type=str, dest="project_name",
                        default="lambda.grnet.gr")

    parser.add_argument('--slaves', type=int, dest='slaves', default=1)
    parser.add_argument('--vcpus_master', type=int, dest='vcpus_master', default=4)
    parser.add_argument('--vcpus_slave', type=int, dest='vcpus_slave', default=4)
    parser.add_argument('--ram_master', type=int, dest='ram_master', default=4096)  # in MB
    parser.add_argument('--ram_slave', type=int, dest='ram_slave', default=4096)  # in MB
    parser.add_argument('--disk_master', type=int, dest='disk_master', default=40)  # in GB
    parser.add_argument('--disk_slave', type=int, dest='disk_slave', default=40)  # in GB
    parser.add_argument('--ip_request', type=int, dest='ip_request', default=1)
    parser.add_argument('--network_request', type=int, dest='network_request', default=1)
    parser.add_argument('--image_name', type=str, dest='image_name', default='debian')
    parser.add_argument('--action', type=str, dest='action', default='create')
    parser.add_argument('--cluster_id', type=int, dest='cluster_id', default=0)

    args = parser.parse_args()
    provisioner = Provisioner(cloud_name=args.cloud)

    if args['action'] == 'create':
        provisioner.create_lambda_cluster('lambda-master', slaves=args.slaves,
                                          vcpus_master=args.vcpus_master,
                                          vcpus_slave=args.vcpus_slave,
                                          ram_master=args.ram_master,
                                          ram_slave=args.ram_slave,
                                          disk_master=args.disk_master,
                                          disk_slave=args.disk_slave,
                                          ip_request=args.ip_request,
                                          network_request=args.network_request,
                                          project_name=args.project_name)

        provisioner_response = provisioner.get_cluster_details()
        master_id = provisioner_response['nodes']['master']['id']
        master_ip = provisioner.get_server_private_ip(master_id)
        provisioner_response['nodes']['master']['internal_ip'] = master_ip
        slave_ids = [slave['id'] for slave in provisioner_response['nodes']['slaves']]
        for i, slave in enumerate(provisioner_response['nodes']['slaves']):
            slave_ip = provisioner.get_server_private_ip(slave['id'])
            provisioner_response['nodes']['slaves'][i]['internal_ip'] = slave_ip
        provisioner_response['pk'] = provisioner.get_private_key()

        print 'response =', provisioner_response
        provisioner_time = time.time()

        manager = Manager(provisioner_response)
        manager.create_inventory()
        # manager.run_playbook(playbook_file=script_path + "/../../ansible/playbooks/test/testinventory.yml", tags=['hosts'])
        # manager.run_playbook(playbook_file=script_path + "/../../ansible/playbooks/test/testproxy.yml", tags=['install'])

        manager.run_playbook(playbook_file=script_path + "/../../ansible/playbooks/cluster-install.yml")

        manager.cleanup()

        provisioner_duration = provisioner_time - start_time
        ansible_duration = time.time() - provisioner_time

        print 'VM provisioning took', round(provisioner_duration), 'seconds'
        print 'Ansible playbooks took', round(ansible_duration), 'seconds'

    elif args['action'] == 'delete':
        details = get_cluster_details(args['cluster_id'])
        if details != None:
            provisioner.delete_lambda_cluster(details)
