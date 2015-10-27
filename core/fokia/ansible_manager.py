import inspect
import os
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
        if 'slaves' in provisioner_response['nodes']:
            self.inventory['slaves'] = []
            for response in provisioner_response['nodes']['slaves']:
                self.inventory['slaves'].append(
                    {'name': 'snf-' + str(response['id']),
                     'ip': response['internal_ip']})
        if 'subnet' in provisioner_response:
            self.cidr = provisioner_response['subnet']['cidr']

        # with tempfile.NamedTemporaryFile(mode='w', delete=False) as kf:
        #     kf.write(provisioner_response['pk'])
        #     self.temp_file = kf.name
        # print self.temp_file
        # ansible.constants.ANSIBLE_SSH_ARGS = '-o "ProxyCommand ssh -o ' \
        #                                      'StrictHostKeyChecking=no -W %%h:%%p ' \
        #                                      'root@%s.vm.okeanos.grnet.gr"' \
        #                                      % (self.inventory['master']['name'])
        ansible.constants.DEFAULT_TIMEOUT = 30
        # ansible.constants.DEFAULT_PRIVATE_KEY_FILE = self.temp_file
        ansible.constants.HOST_KEY_CHECKING = False
        # ansible.constants.DEFAULT_GATHERING = 'explicit'

    def create_inventory(self):
        """
        Create the inventory using the ansible library objects
        :return:
        """

        all_hosts = []

        host = self.inventory['master']
        all_hosts.append(host['name'] + '.vm.okeanos.grnet.gr')
        # ansible_host = ansible.inventory.host.Host(name=all_hosts[-1])
        for host in self.inventory['slaves']:
            all_hosts.append(host['name'] + '.local')
            # ansible_host = ansible.inventory.host.Host(name=all_hosts[-1])
        self.ansible_inventory = ansible.inventory.Inventory(host_list=all_hosts)

        all_group = self.ansible_inventory.get_group('all')
        # all_group.set_variable('ansible_ssh_private_key_file', self.temp_file)
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
                                  {'http_proxy': 'http://' + self.inventory['master']['name'] +
                                                 '.local:3128'})
        # slaves_group.set_variable('http_proxy', 'http://' + self.inventory['master']['name'] +
        # '.local:3128')
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
        playbook_result = pb.run()
        return playbook_result

    def create_master_inventory(self, app_action=None, app_type=None, jar_filename=None):
        master_hostname = self.inventory['master']['name'] + '.vm.okeanos.grnet.gr'
        self.ansible_inventory = ansible.inventory.Inventory(host_list=[master_hostname])
        all_group = self.ansible_inventory.get_group('all')
        master_host = all_group.get_hosts()[0]

        if app_action is not None:
            master_host.set_variable('app_action', app_action)
            master_host.set_variable('app_type', app_type)
            if jar_filename is not None:
                master_host.set_variable('jarfile', jar_filename)

        master_group = ansible.inventory.group.Group(name='master')
        master_group.add_host(master_host)
        self.ansible_inventory.add_group(master_group)
        all_group.add_child_group(master_group)
        return self.ansible_inventory
