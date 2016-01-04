from fokia.ansible_manager import Manager
from mock import patch, MagicMock

from fokia.ansible_manager_minimal import Manager as MiniManager

test_provisioner_response = {
    u'ips':    [{
        u'floating_network_id': u'2186', u'floating_ip_address': u'83.212.116.49',
        u'id':                  u'688160'
    }],
    u'nodes':  {
        u'master': {
            'internal_ip': u'192.168.0.2', u'adminPass': u'0igc3vbnSx', u'id': 666976,
            u'name':       u'test_vm'
        },
        u'slaves': [{'internal_ip': u'192.168.0.3', u'id': 666977, u'name': u'lambda-node1'}]
    },
    u'vpn':    {u'type': u'MAC_FILTERED', u'id': u'143713'},
    'pk':      'Dummy pk',
    u'subnet': {u'cidr': u'192.168.0.0/24', u'gateway_ip': u'192.168.0.1', u'id': u'142761'}
}


def test_playbook_run_minimal_manager():
    with patch('fokia.ansible_manager_minimal.PlayBook') as pb, \
            patch('fokia.ansible_manager_minimal.ansible') as mock_ansible, \
            patch('fokia.ansible_manager_minimal.callbacks') as cb, \
            patch('fokia.ansible_manager_minimal.os'), \
            patch('fokia.ansible_manager_minimal.utils'):
        # Initialize mocks with some test values
        mock_ansible.inventory.Inventory.return_value = MagicMock()
        cb.PlaybookCallbacks.return_value = "a"
        cb.PlaybookRunnerCallbacks.return_value = "b"
        cb.AggregateStats.return_value = "c"

        # Initialize the ansible manager and run a playbook
        manager = MiniManager("test_host", "test_group", "/path/to/private/keys")
        manager.run_playbook(playbook_file="/path/to/playbook.yml",
                             only_tags=["touch"], skip_tags=["touch-2"],
                             extra_vars={
                                 "extra_var_1": "extra_value_1",
                                 "extra_var_2": "extra_value_2",
                                 "extra_var_3": "extra_value_3"
                             })

        # Check playbook was called with the correct arguements
        pb.assert_called_with(only_tags=["touch"], skip_tags=["touch-2"],
                              stats='c', callbacks='a', runner_callbacks='b',
                              playbook='/path/to/playbook.yml',
                              inventory=mock_ansible.inventory.Inventory.return_value,
                              extra_vars={
                                  "extra_var_1": "extra_value_1",
                                  "extra_var_2": "extra_value_2",
                                  "extra_var_3": "extra_value_3"}
                              )


def test_playbook_run():
    with patch('fokia.ansible_manager.PlayBook') as pb, \
            patch('fokia.ansible_manager.callbacks') as cb, \
            patch('fokia.ansible_manager.utils'):
        # Initialize mocks with some test values
        cb.PlaybookCallbacks.return_value = "a"
        cb.PlaybookRunnerCallbacks.return_value = "b"
        cb.AggregateStats.return_value = "c"

        # Initialize a manager, create an inventory and run a playbook
        manager = Manager(test_provisioner_response)
        manager.create_inventory()
        manager.run_playbook(playbook_file="/path/to/playbook.yml",
                             only_tags=["touch"], skip_tags=["touch-2"])

        # Check that playbook was called with the correct argumenets
        pb.asset_called_with(stats='c', only_tags=['touch'], skip_tags=["touch-2"], callbacks='a',
                             playbook='/path/to/playbook.yml', runner_callbacks='b',
                             inventory=manager.inventory)


if __name__ == "__main__":
    test_playbook_run_minimal_manager()
    test_playbook_run()
