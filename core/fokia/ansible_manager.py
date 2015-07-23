import os
import tempfile
import ansible
from ansible.playbook import PlayBook
from ansible import callbacks
from ansible import utils


class Manager:
    def __init__(self, provisioner_response):

        self.inventory = {}
        self.inventory['master'] = {
            'name': 'snf-' + str(provisioner_response['nodes']['master']['id']),
            'ip': provisioner_response['nodes']['master']['internal_ip']}
        self.inventory['slaves'] = []
        for response in provisioner_response['nodes']['slaves']:
            self.inventory['slaves'].append(
                {'name': 'snf-' + str(response['id']),
                 'ip': response['internal_ip']})
        self.cidr = provisioner_response['subnet']['cidr']

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as kf:
            kf.write(provisioner_response['pk'])
            self.temp_file = kf.name
            # print self.temp_file
        ansible.constants.ANSIBLE_SSH_ARGS = '-o "ProxyCommand ssh -i %s -o StrictHostKeyChecking=no -W %%h:%%p root@%s.vm.okeanos.grnet.gr"' \
                                             % (self.temp_file, self.inventory['master']['name'])
        # ansible.constants.DEFAULT_PRIVATE_KEY_FILE = self.temp_file
        ansible.constants.HOST_KEY_CHECKING = False
        ansible.constants.DEFAULT_GATHERING = 'explicit'

    def create_inventory(self):
        """
        Create the inventory using the ansible library objects
        :return:
        """

        all_hosts = []

        host = self.inventory['master']
        all_hosts.append(host['name'] + '.vm.okeanos.grnet.gr')
        ansible_host = ansible.inventory.host.Host(name=all_hosts[-1])
        for host in self.inventory['slaves']:
            all_hosts.append(host['name'] + '.local')
            ansible_host = ansible.inventory.host.Host(name=all_hosts[-1])
        self.ansible_inventory = ansible.inventory.Inventory(host_list=all_hosts)

        all_group = self.ansible_inventory.get_group('all')
        all_group.set_variable('ansible_ssh_private_key_file', self.temp_file)
        all_group.set_variable('local_net', self.cidr)

        all_ansible_hosts = all_group.get_hosts()
        master_group = ansible.inventory.group.Group(name='master')
        master_group.set_variable('proxy_env', {})
        ansible_host = all_ansible_hosts[0]
        ansible_host.set_variable('internal_ip', self.inventory['master']['ip'])
        ansible_host.set_variable('id', 0)
        master_group.add_host(ansible_host)
        self.ansible_inventory.add_group(master_group)
        all_group.add_child_group(master_group)

        slaves_group = ansible.inventory.group.Group(name='slaves')
        slaves_group.set_variable('proxy_env',
                                  {'http_proxy': 'http://' + self.inventory['master']['name'] + '.local:3128'})
        # slaves_group.set_variable('http_proxy', 'http://' + self.inventory['master']['name'] + '.local:3128')
        for host_id, host in enumerate(self.inventory['slaves'], start=1):
            ansible_host = all_ansible_hosts[host_id]
            ansible_host.set_variable('internal_ip', host['ip'])
            ansible_host.set_variable('id', host_id)
            slaves_group.add_host(ansible_host)
        self.ansible_inventory.add_group(slaves_group)
        all_group.add_child_group(slaves_group)

        # print self.ansible_inventory.groups_list()

        return self.ansible_inventory

    def run_playbook(self, playbook_file, tags=None):
        """
        Run the playbook_file using created inventory and tags specified
        :return:
        """
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
        pb = PlayBook(playbook=playbook_file, inventory=self.ansible_inventory, stats=stats,
                      callbacks=playbook_cb,
                      runner_callbacks=runner_cb, only_tags=tags)
        pb.run()

    def cleanup(self):
        os.remove(self.temp_file)


if __name__ == "__main__":
    response = {u'ips': [{u'floating_network_id': u'2216',
                          u'floating_ip_address': u'83.212.118.6',
                          u'id': u'686825'}],
                u'nodes': {u'master': {u'id': 666355,
                                       u'name': u'lambda-master'},
                           u'slaves': [{u'id': 666356, u'name': u'lambda-node1'}]},
                u'vpn': {u'type': u'MAC_FILTERED', u'id': u'143499'},
                u'subnet': {u'cidr': u'192.168.0.0/24', u'gateway_ip': u'192.168.0.1', u'id': u'142564'}}

    manager = Manager(response)
    manager.create_inventory()
    # manager.run_playbook(playbook_file="../../ansible/playbooks/testinventory.yml", tags=['hosts'])
    # manager.run_playbook(playbook_file="../../ansible/playbooks/testproxy.yml", tags=['install'])

    manager.run_playbook(playbook_file="../../ansible/playbooks/wait_for_ssh.yml")
    manager.run_playbook(playbook_file="../../ansible/playbooks/common/install.yml", tags=['master'])
    manager.run_playbook(playbook_file="../../ansible/playbooks/proxy/proxy.yml")
    manager.run_playbook(playbook_file="../../ansible/playbooks/common/install.yml", tags=['slaves'])
    manager.run_playbook(playbook_file="../../ansible/playbooks/apache-hadoop/hadoop-install.yml")
    manager.run_playbook(playbook_file="../../ansible/playbooks/apache-flink/flink-install.yml")
    manager.run_playbook(playbook_file="../../ansible/playbooks/apache-kafka/kafka-install.yml")

    manager.cleanup()
