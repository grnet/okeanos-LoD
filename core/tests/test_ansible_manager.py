from fokia.ansible_manager import Manager
from mock import patch

test_provisioner_response = {
    u'ips': [{u'floating_network_id': u'2186', u'floating_ip_address': u'83.212.116.49', u'id': u'688160'}],
    u'nodes': {
    u'master': {'internal_ip': u'192.168.0.2', u'adminPass': u'0igc3vbnSx', u'id': 666976, u'name': u'test_vm'},
    u'slaves': [{'internal_ip': u'192.168.0.3', u'id': 666977, u'name': u'lambda-node1'}]},
    u'vpn': {u'type': u'MAC_FILTERED', u'id': u'143713'},
    'pk': 'Dummy pk',
    u'subnet': {u'cidr': u'192.168.0.0/24', u'gateway_ip': u'192.168.0.1', u'id': u'142761'}}


def test_playbook_run():
    with patch('fokia.ansible_manager.PlayBook') as pb, patch(
            'fokia.ansible_manager.callbacks') as cb, patch('fokia.ansible_manager.utils') as ut:
        cb.PlaybookCallbacks.return_value = "a"
        cb.PlaybookRunnerCallbacks.return_value = "b"
        cb.AggregateStats.return_value = "c"
        manager = Manager(test_provisioner_response)
        manager.create_inventory()
        manager.run_playbook(playbook_file="../ansible/playbooks/testinventory.yml", tags=["touch"])

    assert pb.call_args[1]['inventory'].groups[0].name == 'master'
    assert pb.call_args[1]['inventory'].groups[1].name == 'slaves'

    assert pb.call_args[1]['inventory'].groups[0].hosts[
               0].name == u'snf-661243.vm.okeanos.grnet.gr'
    assert pb.call_args[1]['inventory'].groups[1].hosts[
               0].name == u'snf-661526.vm.okeanos.grnet.gr'
    assert pb.call_args[1]['inventory'].groups[1].hosts[
               1].name == u'snf-661527.vm.okeanos.grnet.gr'


if __name__ == "__main__":
    test_playbook_run()
