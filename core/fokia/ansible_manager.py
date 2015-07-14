import ansible
from ansible.playbook import PlayBook
from ansible import callbacks
from ansible import utils



class Manager:
    def __init__(self, provisioner_response):

        self.inventory = {}
        self.host_vars = {}
        for group in provisioner_response.keys():
            self.inventory[group] = {"hosts": []}
            for response in provisioner_response[group]:
                self.inventory[group]["hosts"].append(response[u'SNF:fqdn'])
                if group == "masters":
                    self.master_fqdn = response[u'SNF:fqdn'].split('.')[0]

    def create_inventory(self):
        """
        Create the inventory using the ansible library objects
        :return:
        """
        inventory_groups = []
        host_id = 1
        for group in self.inventory.keys():
            inventory_groups.append(ansible.inventory.group.Group(name=group))
            if group != "masters":
                self.host_vars["proxy_env"] = {"http_proxy": "http://"+self.master_fqdn+":3128"}
                self.host_vars["id"] = host_id
                host_id += 1
            for host in self.inventory[group]["hosts"]:
                ansible_host = ansible.inventory.host.Host(name=host)
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


    manager = Manager(test_provisioner_response)
    manager.create_inventory()
   # manager.run_playbook(playbook_file="../../ansible/playbooks/testinventory.yml", tags=["touch"])
    manager.run_playbook(playbook_file="../../ansible/playbooks/testproxy.yml", tags=["install"])
