import ansible
from ansible.playbook import PlayBook
from ansible import callbacks
from ansible import utils

responses = {"masters": [{u'addresses': {}, u'links': [
    {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664', u'rel': u'self'},
    {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664', u'rel': u'bookmark'}],
                          u'image': {u'id': u'0e399015-8723-4c78-8198-75bdf693cdde', u'links': [{
                              u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                              u'rel': u'self'}, {
                              u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                              u'rel': u'bookmark'}, {
                              u'href': u'https://cyclades.okeanos.grnet.gr/image/v1.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                              u'rel': u'alternate'}]},
                          u'suspended': False, u'flavor': {u'id': 3, u'links': [
    {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3', u'rel': u'self'},
    {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3', u'rel': u'bookmark'}]}, u'id': 664664,
                          u'security_groups': [{u'name': u'default'}], u'attachments': [],
                          u'user_id': u'19e4daba-20e2-4d57-a6aa-92ba1c982fd9', u'accessIPv4': u'', u'accessIPv6': u'',
                          u'progress': 0, u'config_drive': u'', u'status': u'BUILD',
                          u'updated': u'2015-07-08T10:15:38.936455+00:00', u'hostId': u'',
                          u'SNF:fqdn': u'snf-661243.vm.okeanos.grnet.gr', u'deleted': False, u'key_name': None,
                          u'name': u'to mikro debian sto livadi', u'adminPass': u'X9yqjSTAFO',
                          u'tenant_id': u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f',
                          u'created': u'2015-07-08T10:15:37.837229+00:00', u'SNF:task_state': u'BUILDING',
                          u'volumes': [50369], u'diagnostics': [],
                          u'metadata': {u'os': u'debian', u'users': u'root ckaner'}, u'SNF:port_forwarding': {}}],
             "slaves": [{u'addresses': {}, u'links': [
                 {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664', u'rel': u'self'},
                 {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664', u'rel': u'bookmark'}],
                         u'image': {u'id': u'0e399015-8723-4c78-8198-75bdf693cdde', u'links': [{
                             u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                             u'rel': u'self'}, {
                             u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                             u'rel': u'bookmark'}, {
                             u'href': u'https://cyclades.okeanos.grnet.gr/image/v1.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                             u'rel': u'alternate'}]},
                         u'suspended': False, u'flavor': {u'id': 3, u'links': [
                 {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3', u'rel': u'self'},
                 {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3', u'rel': u'bookmark'}]},
                         u'id': 664664, u'security_groups': [{u'name': u'default'}], u'attachments': [],
                         u'user_id': u'19e4daba-20e2-4d57-a6aa-92ba1c982fd9', u'accessIPv4': u'', u'accessIPv6': u'',
                         u'progress': 0, u'config_drive': u'', u'status': u'BUILD',
                         u'updated': u'2015-07-08T10:15:38.936455+00:00', u'hostId': u'',
                         u'SNF:fqdn': u'snf-661526.vm.okeanos.grnet.gr', u'deleted': False, u'key_name': None,
                         u'name': u'to mikro debian sto livadi', u'adminPass': u'X9yqjSTAFO',
                         u'tenant_id': u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f',
                         u'created': u'2015-07-08T10:15:37.837229+00:00', u'SNF:task_state': u'BUILDING',
                         u'volumes': [50369], u'diagnostics': [],
                         u'metadata': {u'os': u'debian', u'users': u'root ckaner'}, u'SNF:port_forwarding': {}},
                        {u'addresses': {}, u'links': [
                            {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664',
                             u'rel': u'self'},
                            {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/664664',
                             u'rel': u'bookmark'}], u'image': {u'id': u'0e399015-8723-4c78-8198-75bdf693cdde',
                                                               u'links': [{
                                                                   u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                                                                   u'rel': u'self'}, {
                                                                   u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                                                                   u'rel': u'bookmark'}, {
                                                                   u'href': u'https://cyclades.okeanos.grnet.gr/image/v1.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
                                                                   u'rel': u'alternate'}]}, u'suspended': False,
                         u'flavor': {u'id': 3, u'links': [
                             {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3', u'rel': u'self'},
                             {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                              u'rel': u'bookmark'}]}, u'id': 664664, u'security_groups': [{u'name': u'default'}],
                         u'attachments': [], u'user_id': u'19e4daba-20e2-4d57-a6aa-92ba1c982fd9', u'accessIPv4': u'',
                         u'accessIPv6': u'', u'progress': 0, u'config_drive': u'', u'status': u'BUILD',
                         u'updated': u'2015-07-08T10:15:38.936455+00:00', u'hostId': u'',
                         u'SNF:fqdn': u'snf-661527.vm.okeanos.grnet.gr', u'deleted': False, u'key_name': None,
                         u'name': u'to mikro debian sto livadi', u'adminPass': u'X9yqjSTAFO',
                         u'tenant_id': u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f',
                         u'created': u'2015-07-08T10:15:37.837229+00:00', u'SNF:task_state': u'BUILDING',
                         u'volumes': [50369], u'diagnostics': [],
                         u'metadata': {u'os': u'debian', u'users': u'root ckaner'}, u'SNF:port_forwarding': {}}]}


class Manager:
    def __init__(self):

        self.inventory = {}
        for group in responses.keys():
            self.inventory[group] = {"hosts": []}
            for response in responses[group]:
                self.inventory[group]["hosts"].append(response[u'SNF:fqdn'])

    def create_inventory(self):
        inventory_groups = []
        for group in self.inventory.keys():
            inventory_groups.append(ansible.inventory.group.Group(name=group))
            # print inventory[group]
            for host in self.inventory[group]["hosts"]:
                ansible_host = ansible.inventory.host.Host(name=host)
                inventory_groups[-1].add_host(ansible_host)

        self.inventory = ansible.inventory.Inventory()
        for group in inventory_groups:
            self.inventory.add_group(group)

    def run_playbook(self, playbook_file, tags):
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
        pb = PlayBook(playbook=playbook_file, inventory=self.inventory, stats=stats, callbacks=playbook_cb,
                      runner_callbacks=runner_cb, only_tags=tags)
        pb.run()


if __name__ == "__main__":
        manager = Manager()
        manager.create_inventory()
        manager.run_playbook(playbook_file="../ansible/playbooks/test.yml", tags=["touch"])