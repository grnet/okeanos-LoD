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

        self.kf = tempfile.NamedTemporaryFile()
        self.kf.write(provisioner_response['pk'])

        ansible.constants.ANSIBLE_SSH_ARGS = '-o "ProxyCommand ssh -A -W %%h:%%p root@%s" -i %s' \
                                             % self.inventory['master']['name'] + 'vm.okeanos.grnet.gr' %self.kf.name
        # ansible.constants.ANSIBLE_SSH_ARGS = '-o "ProxyCommand ssh root@%s nc %%h %%p"' \
        #                                      % self.inventory["master"]["name"] + "vm.okeanos.grnet.gr"
        ansible.constants.HOST_KEY_CHECKING = False
        ansible.constants.DEFAULT_GATHERING = 'explicit'

    def create_inventory(self):
        """
        Create the inventory using the ansible library objects
        :return:
        """

        inventory_groups = []
        host_vars = {}

        master_group = ansible.inventory.group.Group(name='master')
        host = self.inventory['master']
        ansible_host = ansible.inventory.host.Host(name=host['name'] + '.vm.okeanos.grnet.gr')
        host_vars['internal_ip'] = self.inventory['master']['ip']
        host_vars['local_net'] = self.cidr
        for var_key, var_value in host_vars.iteritems():
            ansible_host.set_variable(var_key, var_value)
        ansible_host.set_variable('id', 0)
        master_group.add_host(ansible_host)
        inventory_groups.append(master_group)

        slave_group = ansible.inventory.group.Group(name='slaves')
        host_vars['proxy_env'] = {'http_proxy': 'http://' + self.inventory['master']['name']+'.local:3128'}
        for host_id, host in enumerate(self.inventory["slaves"], start=1):
            ansible_host = ansible.inventory.host.Host(name=host['name'] + '.local')
            host_vars['internal_ip'] = host['ip']
            for var_key, var_value in host_vars.iteritems():
                ansible_host.set_variable(var_key, var_value)
            ansible_host.set_variable('id', host_id)
            slave_group.add_host(ansible_host)
        inventory_groups.append(slave_group)

        self.ansible_inventory = ansible.inventory.Inventory(host_list=None)
        for group in inventory_groups:
            self.ansible_inventory.add_group(group)

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


if __name__ == "__main__":

    response = {u'ips': [{u'floating_network_id': u'2216',
                          u'floating_ip_address': u'83.212.118.6',
                          u'id': u'686825'}],
                u'nodes': {u'master': {u'id': 666355,
                                       u'name': u'lambda-master'},
                           u'slaves': [{u'id': 666356, u'name': u'lambda-node1'}]},
                u'vpn': {u'type': u'MAC_FILTERED', u'id': u'143499'},
                u'subnet': {u'cidr': u'192.168.0.0/24', u'gateway_ip': u'192.168.0.1', u'id': u'142564'}}

