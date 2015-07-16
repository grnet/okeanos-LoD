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

    def create_inventory(self):
        """
        Create the inventory using the ansible library objects
        :return:
        """

        ipdict = {"snf-661243": "192.168.0.2", "snf-661526" : "192.168.0.3", "snf-661527" : "192.168.0.4"}
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

    inv = test_provisioner_response = \
    {"master": [{u'addresses': {}, u'links': [
        {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664',
         u'rel': u'self'},
        {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664',
         u'rel': u'bookmark'}],
                  u'image': {
                      u'id': u'0e399015-8723-4c78-8198-75bdf693cdde',
                      u'links': [{
                          u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                          u'rel': u'self'}, {
                          u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                          u'rel': u'bookmark'}, {
                          u'href': u'https://cyclades.okeanos.grnet.gr/image/v1.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                          u'rel': u'alternate'}]},
                  u'suspended': False,
                  u'flavor': {u'id': 3, u'links': [
                      {
                          u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                          u'rel': u'self'},
                      {
                          u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                          u'rel': u'bookmark'}]},
                  u'id': 664664,
                  u'security_groups': [{u'name': u'default'}],
                  u'attachments': [],
                  u'user_id': u'19e4daba-20e2-4d57-a6aa-92ba1c982fd9',
                  u'accessIPv4': u'', u'accessIPv6': u'',
                  u'progress': 0, u'config_drive': u'',
                  u'status': u'BUILD',
                  u'updated': u'2015-07-08T10:15:38.936455+00:00',
                  u'hostId': u'',
                  u'SNF:fqdn': u'snf-661243.vm.okeanos.grnet.gr',
                  u'deleted': False, u'key_name': None,
                  u'name': u'to mikro debian sto livadi',
                  u'adminPass': u'X9yqjSTAFO',
                  u'tenant_id': u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f',
                  u'created': u'2015-07-08T10:15:37.837229+00:00',
                  u'SNF:task_state': u'BUILDING',
                  u'volumes': [50369], u'diagnostics': [],
                  u'metadata': {u'os': u'debian',
                                u'users': u'root ckaner'},
                  u'SNF:port_forwarding': {}}],
     "slaves": [{u'addresses': {}, u'links': [
         {
             u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664',
             u'rel': u'self'},
         {
             u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664',
             u'rel': u'bookmark'}],
                 u'image': {
                     u'id': u'0e399015-8723-4c78-8198-75bdf693cdde',
                     u'links': [{
                         u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                         u'rel': u'self'}, {
                         u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                         u'rel': u'bookmark'}, {
                         u'href': u'https://cyclades.okeanos.grnet.gr/image/v1.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                         u'rel': u'alternate'}]},
                 u'suspended': False,
                 u'flavor': {u'id': 3, u'links': [
                     {
                         u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                         u'rel': u'self'},
                     {
                         u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                         u'rel': u'bookmark'}]},
                 u'id': 664664,
                 u'security_groups': [{u'name': u'default'}],
                 u'attachments': [],
                 u'user_id': u'19e4daba-20e2-4d57-a6aa-92ba1c982fd9',
                 u'accessIPv4': u'', u'accessIPv6': u'',
                 u'progress': 0, u'config_drive': u'',
                 u'status': u'BUILD',
                 u'updated': u'2015-07-08T10:15:38.936455+00:00',
                 u'hostId': u'',
                 u'SNF:fqdn': u'snf-661526.vm.okeanos.grnet.gr',
                 u'deleted': False, u'key_name': None,
                 u'name': u'to mikro debian sto livadi',
                 u'adminPass': u'X9yqjSTAFO',
                 u'tenant_id': u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f',
                 u'created': u'2015-07-08T10:15:37.837229+00:00',
                 u'SNF:task_state': u'BUILDING',
                 u'volumes': [50369], u'diagnostics': [],
                 u'metadata': {u'os': u'debian',
                               u'users': u'root ckaner'},
                 u'SNF:port_forwarding': {}},
                {u'addresses': {}, u'links': [
                    {
                        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664',
                        u'rel': u'self'},
                    {
                        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664',
                        u'rel': u'bookmark'}], u'image': {
                    u'id': u'0e399015-8723-4c78-8198-75bdf693cdde',
                    u'links': [{
                        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                        u'rel': u'self'}, {
                        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                        u'rel': u'bookmark'}, {
                        u'href': u'https://cyclades.okeanos.grnet.gr/image/v1.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                        u'rel': u'alternate'}]},
                 u'suspended': False,
                 u'flavor': {u'id': 3, u'links': [
                     {
                         u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                         u'rel': u'self'},
                     {
                         u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                         u'rel': u'bookmark'}]},
                 u'id': 664664,
                 u'security_groups': [{u'name': u'default'}],
                 u'attachments': [],
                 u'user_id': u'19e4daba-20e2-4d57-a6aa-92ba1c982fd9',
                 u'accessIPv4': u'',
                 u'accessIPv6': u'', u'progress': 0,
                 u'config_drive': u'', u'status': u'BUILD',
                 u'updated': u'2015-07-08T10:15:38.936455+00:00',
                 u'hostId': u'',
                 u'SNF:fqdn': u'snf-661527.vm.okeanos.grnet.gr',
                 u'deleted': False, u'key_name': None,
                 u'name': u'to mikro debian sto livadi',
                 u'adminPass': u'X9yqjSTAFO',
                 u'tenant_id': u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f',
                 u'created': u'2015-07-08T10:15:37.837229+00:00',
                 u'SNF:task_state': u'BUILDING',
                 u'volumes': [50369], u'diagnostics': [],
                 u'metadata': {u'os': u'debian',
                               u'users': u'root ckaner'},
                 u'SNF:port_forwarding': {}}]}


    from provisioner import Provisioner
    # provisioner = Provisioner("lambda")
    # inv = provisioner.create_lambda_cluster("test_vm")

    manager = Manager(inv)
    manager.create_inventory()
    manager.run_playbook(playbook_file="../../ansible/playbooks/testinventory.yml")
    # manager.run_playbook(playbook_file="../../ansible/playbooks/testproxy.yml", tags=["install"])
