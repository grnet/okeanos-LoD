from mock import patch, MagicMock

from fokia.vm_manager import VM_Manager

test_flavors = [{
    u'SNF:allow_create': True,
    u'SNF:disk_template': u'drbd',
    u'SNF:volume_type': 1,
    u'disk': 20,
    u'id': 1,
    u'links': [
        {
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/1',
            u'rel': u'self'
        },
        {
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/1',
            u'rel': u'bookmark'
        }],
    u'name': u'C1R1024D20drbd',
    u'ram': 1024,
    u'vcpus': 1
},
    {
        u'SNF:allow_create': True,
        u'SNF:disk_template': u'drbd',
        u'SNF:volume_type': 1,
        u'disk': 40,
        u'id': 3,
        u'links': [
            {
                u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                u'rel': u'self'
            },
            {
                u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                u'rel': u'bookmark'
            }],
        u'name': u'C1R1024D40drbd',
        u'ram': 1024,
        u'vcpus': 1
},
    {
        u'SNF:allow_create': True,
        u'SNF:disk_template': u'drbd',
        u'SNF:volume_type': 1,
        u'disk': 20,
        u'id': 4,
        u'links': [
            {
                u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/4',
                u'rel': u'self'
            },
            {
                u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/4',
                u'rel': u'bookmark'
            }],
        u'name': u'C1R2048D20drbd',
        u'ram': 2048,
        u'vcpus': 1
}]

test_quotas = {
    u'234f23f42234f':
        {
            u'astakos.pending_app': {
                u'limit': 0,
                u'pending': 0,
                u'project_limit': 0,
                u'project_pending': 0,
                u'project_usage': 0,
                u'usage': 0
            },
            u'cyclades.cpu': {
                u'limit': 112,
                u'pending': 0,
                u'project_limit': 112,
                u'project_pending': 0,
                u'project_usage': 50,
                u'usage': 0
            },
            u'cyclades.disk': {
                u'limit': 1073741824000,
                u'pending': 0,
                u'project_limit': 1073741824000,
                u'project_pending': 0,
                u'project_usage': 450971566080,
                u'usage': 0
            },
            u'cyclades.floating_ip': {
                u'limit': 26,
                u'pending': 0,
                u'project_limit': 26,
                u'project_pending': 0,
                u'project_usage': 19,
                u'usage': 1
            },
            u'cyclades.network.private': {
                u'limit': 20,
                u'pending': 0,
                u'project_limit': 20,
                u'project_pending': 0,
                u'project_usage': 11,
                u'usage': 0
            },
            u'cyclades.ram': {
                u'limit': 163208757248,
                u'pending': 0,
                u'project_limit': 163208757248,
                u'project_pending': 0,
                u'project_usage': 55834574848,
                u'usage': 0
            },
            u'cyclades.vm': {
                u'limit': 150,
                u'pending': 0,
                u'project_limit': 150,
                u'project_pending': 0,
                u'project_usage': 13,
                u'usage': 0
            },
            u'pithos.diskspace': {
                u'limit': 107374182400,
                u'pending': 0,
                u'project_limit': 107374182400,
                u'project_pending': 0,
                u'project_usage': 2859011176,
                u'usage': 0
            }
        }
}


def test_create_single_vm():
    with patch('fokia.provisioner_base.astakos') as astakos, \
            patch('fokia.provisioner_base.KamakiConfig'), \
            patch('fokia.provisioner_base.cyclades') as cyclades, \
            patch('fokia.provisioner_base.os.path.exists') as mock_exists, \
            patch('fokia.vm_manager.open', create=True) as mock_open:
        # Initialize mocks that will be used
        mock_open.return_value = MagicMock(spec=file)
        mock_open.return_value.__enter__.return_value.read.return_value = "asdkjahgsdih3"
        cyclades.CycladesNetworkClient().create_floatingip.return_value = {
            "floating_network_id": "uh12dh912d", "floating_ip_address": "192.168.0.12"
        }
        cyclades.CycladesComputeClient().list_flavors.return_value = test_flavors
        mock_exists.return_value = True
        astakos.AstakosClient().get_projects.return_value = [{'id': '234f23f42234f'}]
        astakos.AstakosClient().get_quotas.return_value = test_quotas

        # Initialize a vm_manager instance
        manager = VM_Manager(None, "lambda")

        # Create vm with some specific parameters
        manager.create_single_vm("test_name", wait=False,
                                 vcpus=1, ram=1024, disk=40,
                                 project_name="test_proj",
                                 public_key_path="public/key/path.pub")

        manager.destroy('test_vm_id')

        # Check the mocked cyclades call to make sure it was called with the intended parameters
        manager.cyclades.create_server. \
            assert_called_with(**{
                'name': 'test_name',
                'image_id':
                    u'0ad78ab6-d3cd-42c9-8922-9cf63bbb7539',
                'flavor_id': 3,
                'project_id': '234f23f42234f',
                'networks': [
                    {
                        u'fixed_ip': '192.168.0.12',
                        u'uuid': 'uh12dh912d'
                    }],
                'personality': [{
                    'owner': 'root',
                    'path': '/root/.ssh/authorized_keys',
                    'group': 'root',
                    'mode': 384,
                    'contents': 'YXNka2phaGdzZGloMw=='
                }]
            })

        manager.cyclades.delete_server.assert_called_with('test_vm_id')


if __name__ == '__main__':
    test_create_single_vm()
