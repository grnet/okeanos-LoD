from fokia.ansible_manager import Manager
from mock import patch

test_provisioner_response = \
    {"masters": [{u'addresses': {}, u'links': [
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


def test_playbook_run():
    with patch('fokia.ansible_manager.PlayBook') as pb, patch(
            'fokia.ansible_manager.callbacks') as cb, patch('fokia.ansible_manager.utils') as ut:
        cb.PlaybookCallbacks.return_value = "a"
        cb.PlaybookRunnerCallbacks.return_value = "b"
        cb.AggregateStats.return_value = "c"
        manager = Manager(test_provisioner_response)
        manager.create_inventory()
        manager.run_playbook(playbook_file="../ansible/playbooks/test.yml", tags=["touch"])

    assert pb.call_args[1]['inventory'].groups[0].name == 'masters'
    assert pb.call_args[1]['inventory'].groups[1].name == 'slaves'

    assert pb.call_args[1]['inventory'].groups[0].hosts[
               0].name == u'snf-661243.vm.okeanos.grnet.gr'
    assert pb.call_args[1]['inventory'].groups[1].hosts[
               0].name == u'snf-661526.vm.okeanos.grnet.gr'
    assert pb.call_args[1]['inventory'].groups[1].hosts[
               1].name == u'snf-661527.vm.okeanos.grnet.gr'


if __name__ == "__main__":
    test_playbook_run()
