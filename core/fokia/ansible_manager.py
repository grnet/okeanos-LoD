import ansible
from ansible.playbook import PlayBook
from ansible import callbacks
from ansible import utils



class Manager:
    def __init__(self, provisioner_response):

        self.inventory = {}
        self.host_vars = {}
        for group in provisioner_response.keys():
            if group == "masters":
                self.master_fqdn = response[u'SNF:fqdn']
            self.inventory[group] = {"hosts": []}
            for response in provisioner_response[group]:
                self.inventory[group]["hosts"].append(response[u'SNF:fqdn'])

    def create_inventory(self):
        """
        Create the inventory using the ansible library objects
        :return:
        """
        inventory_groups = []
        for group in self.inventory.keys():
            inventory_groups.append(ansible.inventory.group.Group(name=group))
            if group != "masters":
                self.host_vars["http_proxy"] = "http://"+self.master_fqdn+":3128"
            for host in self.inventory[group]["hosts"]:
                ansible_host = ansible.inventory.host.Host(name=host)
                host_vars = self.host_vars.iteritems()
                for var_key, var_value in self.host_vars.iteritems():
                    ansible_host.set_variable(var_key, var_value)
                inventory_groups[-1].add_host(ansible_host)

        self.inventory = ansible.inventory.Inventory(host_list=None)
        for group in inventory_groups:
            self.inventory.add_group(group)

        return self.inventory

    def run_playbook(self, playbook_file, tags):
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
    manager = Manager()
    manager.create_inventory()
    manager.run_playbook(playbook_file="../ansible/playbooks/test.yml", tags=["touch"])
