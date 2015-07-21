import argparse
import time
from provisioner import Provisioner
from ansible_manager import Manager

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Okeanos VM provisioning")
    parser.add_argument('--cloud', type=str, dest="cloud", default="lambda")
    parser.add_argument('--project-name', type=str, dest="project_name",
                        default="lambda.grnet.gr")
    parser.add_argument('--name', type=str, dest='name', default="to mikro debian sto livadi")


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
    parser.add_argument('--cluster_size', type=int, dest='cluster_size', default=2)

    args = parser.parse_args()
    provisioner = Provisioner(cloud_name=args.cloud)
    provisioner.create_lambda_cluster('test_vm', slaves=args.slaves,
                                              cluster_size=args.cluster_size,
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

    print provisioner_response

    time.sleep(15)
    manager = Manager(provisioner_response)
    manager.create_inventory()
    manager.run_playbook(playbook_file="../../ansible/playbooks/testinventory.yml", tags=['hosts'])
    # manager.run_playbook(playbook_file="../../ansible/playbooks/testproxy.yml", tags=['install'])

    # manager.run_playbook(playbook_file="../../ansible/playbooks/common/install.yml", tags=['master'])
    # manager.run_playbook(playbook_file="../../ansible/playbooks/proxy/proxy.yml")
    # manager.run_playbook(playbook_file="../../ansible/playbooks/common/install.yml", tags=['slaves'])

    # INSERT PLAYBOOKS HERE

    manager.cleanup()
