import ansible
from ansible.playbook import PlayBook
from ansible import callbacks
from ansible import utils



class Manager:
    def __init__(self, provisioner_response):

        self.inventory = {}
        for group in provisioner_response.keys():
            self.inventory[group] = {"hosts": []}
            for response in provisioner_response[group]:
                self.inventory[group]["hosts"].append(response[u'SNF:fqdn'])
                if group == "master":
                    self.master_fqdn = response[u'SNF:fqdn'].split('.')[0]

    def create_inventory(self, private_ips):
        """
        Create the inventory using the ansible library objects
        :return:
        """


        inventory_groups = []
        host_vars = {}

        master_group = ansible.inventory.group.Group(name="master")
        host = self.inventory["master"]["hosts"][0]
        ansible_host = ansible.inventory.host.Host(name=host)
        host_vars["internal_ip"] = ipdict[host.split('.')[0]]
        for var_key, var_value in host_vars.iteritems():
            ansible_host.set_variable(var_key, var_value)
        ansible_host.set_variable("id", 0)
        master_group.add_host(ansible_host)
        inventory_groups.append(master_group)

        slave_group = ansible.inventory.group.Group(name="slaves")
        host_vars["proxy_env"] = {"http_proxy": "http://"+self.master_fqdn+":3128"}
        for host_id, host in enumerate(self.inventory["slaves"]["hosts"], start=1):
            ansible_host = ansible.inventory.host.Host(name=host)
            host_vars["internal_ip"] = ipdict[host.split('.')[0]]
            for var_key, var_value in host_vars.iteritems():
                ansible_host.set_variable(var_key, var_value)
            ansible_host.set_variable("id", host_id)
            slave_group.add_host(ansible_host)
        inventory_groups.append(slave_group)

        self.inventory = ansible.inventory.Inventory(host_list=None)
        for group in inventory_groups:
            self.inventory.add_group(group)

        return self.inventory

    def run_playbook(self, playbook_file, tags=None):
        """
        Run the playbook_file using created inventory and tags specified
        :return:
        """
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
        pb = PlayBook(playbook=playbook_file, inventory=self.inventory, stats=stats,
                      callbacks=playbook_cb,
                      runner_callbacks=runner_cb, only_tags=tags)
        pb.run()


if __name__ == "__main__":

    from provisioner import Provisioner
    provisioner = Provisioner("lambda")
    inv = provisioner.create_lambda_cluster("test_vm")

    manager = Manager(inv, provisioner)
    manager.create_inventory(provisioner.get_server_private_ip())
   # manager.run_playbook(playbook_file="../../ansible/playbooks/testinventory.yml", tags=["touch"])
    manager.run_playbook(playbook_file="../../ansible/playbooks/testproxy.yml", tags=["install"])
