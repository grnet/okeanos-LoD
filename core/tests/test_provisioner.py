import mock
from mock import call
import pytest
from fokia.provisioner import Provisioner
from kamaki.clients import ClientError

test_flavors = [{
    u'SNF:allow_create': True, u'SNF:disk_template': u'drbd', u'SNF:volume_type': 1, u'disk': 20,
    u'id': 1, u'links': [
        {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/1', u'rel': u'self'}, {
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/1',
            u'rel': u'bookmark'
        }], u'name': u'C1R1024D20drbd', u'ram': 1024, u'vcpus': 1
}, {
    u'SNF:allow_create': True, u'SNF:disk_template': u'drbd', u'SNF:volume_type': 1, u'disk': 40,
    u'id': 3, u'links': [
        {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3', u'rel': u'self'}, {
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
            u'rel': u'bookmark'
        }], u'name': u'C1R1024D40drbd', u'ram': 1024, u'vcpus': 1
}, {
    u'SNF:allow_create': True, u'SNF:disk_template': u'drbd', u'SNF:volume_type': 1, u'disk': 20,
    u'id': 4, u'links': [
        {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/4', u'rel': u'self'}, {
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/4',
            u'rel': u'bookmark'
        }], u'name': u'C1R2048D20drbd', u'ram': 2048, u'vcpus': 1
}]

test_images = [{
    u'created': u'2015-06-26T11:29:59+00:00',
    u'id': u'0ad78ab6-d3cd-42c9-8922-9cf63bbb7539', u'is_snapshot': False,
    u'links': [
        {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/1232', u'rel': u'self'}, {
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/234d',
            u'rel': u'bookmark'
        }, {
            u'href': u'https://cyclades.okeanos.grnet.gr/image/v1.0/images/345',
            u'rel': u'alternate'
        }], u'metadata': {
        u'description': u'ArchLinux 2015.06.26 with openssh and iptables setup',
        u'gui': u'No GUI', u'kernel': u'4.0.6-1', u'os': u'archlinux',
        u'osfamily': u'linux', u'partition_table': u'gpt', u'root_partition': u'1',
        u'sortorder': u'7400000', u'users': u'root'
    }, u'name': u'archlinux-2015.06.26', u'progress': 100, u'public': True,
    u'status': u'ACTIVE', u'tenant_id': u'7e271a0b-1427-45ec-9916-f8e72bfbf3d4',
    u'updated': u'2015-06-26T11:29:59+00:00',
    u'user_id': u'7e271a0b-1427-45ec-9916-f8e72bfbf3d4'
}, {
    u'created': u'2014-03-11T12:55:07+00:00',
    u'id': u'0099593e-4f6d-48bf-8f03-0cec7fabb05b', u'is_snapshot': False,
    u'links': [
        {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/123', u'rel': u'self'}, {
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/2345',
            u'rel': u'bookmark'
        }, {
            u'href': u'https://cyclades.okeanos.grnet.gr/image/v1.0/images/3456',
            u'rel': u'alternate'
        }], u'metadata': {
        u'description': u'Master clone', u'os': u'ubuntu', u'osfamily': u'linux',
        u'partition_table': u'msdos', u'root_partition': u'1', u'users': u'user hduser'
    }, u'name': u'master_clone', u'progress': 100, u'public': True,
    u'status': u'ACTIVE', u'tenant_id': u'607bc20e-ae01-46ca-8a7d-d37b92e9908f',
    u'updated': u'2014-03-11T12:55:07+00:00',
    u'user_id': u'607bc20e-ae01-46ca-8a7d-d37b92e9908f'
}]

test_projects = [{
    u'creation_date': u'2015-06-09T09:46:44.327826+00:00', u'description': u'',
    u'end_date': u'2015-11-30T00:00:00+00:00', u'homepage': u'',
    u'id': u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f',
    u'join_policy': u'moderated', u'leave_policy': u'auto',
    u'max_members': 9223372036854775807, u'name': u'lambda.grnet.gr',
    u'owner': u'69c6686c-4e3e-407e-96b4-c21ef7d5def5', u'private': False,
    u'resources': {
        u'astakos.pending_app': {
            u'member_capacity': 0, u'project_capacity': 0
        }, u'cyclades.cpu': {
            u'member_capacity': 80, u'project_capacity': 80
        }, u'cyclades.disk': {
            u'member_capacity': 1073741824000, u'project_capacity': 1073741824000
        }, u'cyclades.floating_ip': {
            u'member_capacity': 10, u'project_capacity': 10
        }, u'cyclades.network.private': {
            u'member_capacity': 5, u'project_capacity': 5
        }, u'cyclades.ram': {
            u'member_capacity': 128849018880, u'project_capacity': 128849018880
        }, u'cyclades.vm': {
            u'member_capacity': 20, u'project_capacity': 20
        }, u'pithos.diskspace': {
            u'member_capacity': 0, u'project_capacity': 0
        }
    }, u'state': u'active', u'system_project': False
}]

test_quotas = {
    '6ff62e8e-0ce9-41f7-ad99-13a18ecada5f': {
        'cyclades.disk': {
            'project_limit': 1288490188800, 'project_pending': 0, 'project_usage': 64424509440,
            'usage': 0, 'limit': 322122547200, 'pending': 0
        }, 'cyclades.vm': {
            'project_limit': 60, 'project_pending': 0, 'project_usage': 2, 'usage': 0, 'limit': 150,
            'pending': 0
        }, 'pithos.diskspace': {
            'project_limit': 429496729600, 'project_pending': 0, 'project_usage': 0, 'usage': 0,
            'limit': 107374182400, 'pending': 0
        }, 'cyclades.ram': {
            'project_limit': 128849018880, 'project_pending': 0, 'project_usage': 12884901888,
            'usage': 0, 'limit': 32212254720, 'pending': 0
        }, 'cyclades.cpu': {
            'project_limit': 120, 'project_pending': 0, 'project_usage': 12, 'usage': 0,
            'limit': 30, 'pending': 0
        }, 'cyclades.floating_ip': {
            'project_limit': 10, 'project_pending': 0, 'project_usage': 6, 'usage': 3, 'limit': 4,
            'pending': 0
        }, 'cyclades.network.private': {
            'project_limit': 30, 'project_pending': 0, 'project_usage': 7, 'usage': 0, 'limit': 4,
            'pending': 0
        }, 'astakos.pending_app': {
            'project_limit': 0, 'project_pending': 0, 'project_usage': 0, 'usage': 0, 'limit': 0,
            'pending': 0
        }
    }
}

test_ip = {
    u'floating_network_id': u'2186', u'user_id': u'9819231a-e9e2-40f7-93f1-e2e4cb50cc33',
    u'deleted': False, u'tenant_id': u'9819231a-e9e2-40f7-93f1-e2e4cb50cc33',
    u'instance_id': None, u'fixed_ip_address': None,
    u'floating_ip_address': u'83.212.116.58', u'port_id': None, u'id': u'684011'
}

test_vm = {
    u'addresses': {}, u'links': [{
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/665007', u'rel': u'self'
    }, {
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/servers/665007',
        u'rel': u'bookmark'
    }], u'image': {
        u'id': u'0e399015-8723-4c78-8198-75bdf693cdde', u'links': [{
            u'href':
                u'https://cyclades.okeanos.grnet.gr/compute/'
                u'v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
            u'rel': u'self'
        }, {
            u'href':
                u'https://cyclades.okeanos.grnet.gr/compute/'
                u'v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
            u'rel': u'bookmark'
        }, {
            u'href':
                u'https://cyclades.okeanos.grnet.gr/image/'
                u'v1.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
            u'rel': u'alternate'
        }]
    }, u'suspended': False, u'flavor': {
        u'id': 3, u'links': [
            {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3', u'rel': u'self'},
            {
                u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                u'rel': u'bookmark'
            }]
    }, u'id': 665007, u'security_groups': [{u'name': u'default'}], u'attachments': [],
    u'user_id': u'9819231a-e9e2-40f7-93f1-e2e4cb50cc33', u'accessIPv4': u'',
    u'accessIPv6': u'', u'progress': 0, u'config_drive': u'', u'status': u'BUILD',
    u'updated': u'2015-07-10T07:13:25.973280+00:00', u'hostId': u'',
    u'SNF:fqdn': u'snf-665007.vm.okeanos.grnet.gr', u'deleted': False, u'key_name': None,
    u'name': u'to mikro debian sto livadi', u'adminPass': u'q0WVXWIjc4',
    u'tenant_id': u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f',
    u'created': u'2015-07-10T07:13:24.862714+00:00', u'SNF:task_state': u'BUILDING',
    u'volumes': [50722], u'diagnostics': [],
    u'metadata': {u'os': u'debian', u'users': u'root ckaner'}, u'SNF:port_forwarding': {}
}


def test_find_flavor():
    with mock.patch('fokia.provisioner_base.astakos'), \
         mock.patch('fokia.provisioner_base.KamakiConfig'), \
         mock.patch('fokia.provisioner_base.cyclades'), \
         mock.patch('fokia.provisioner_base.os.path.exists') as mock_exists:
        mock_exists.return_value = True
        provisioner = Provisioner(None, "lambda")
        provisioner.astakos.get_projects.return_value = test_projects
        provisioner.cyclades.list_images.return_value = test_images
        provisioner.cyclades.list_flavors.return_value = test_flavors
        provisioner.image_id = u'0ad78ab6-d3cd-42c9-8922-9cf63bbb7539'
        provisioner.create_vm(vm_name="tost", project_name="lambda.grnet.gr",
                              project_mode="supahpower", image_name="archlinux", net_id="12345",
                              flavor={'id': 3})
        provisioner.cyclades.create_server. \
            assert_called_with(flavor_id=3,
                               image_id=u'0ad78ab6-d3cd-42c9-8922-9cf63bbb7539',
                               name='tost',
                               networks=[{u'uuid': '12345'}],
                               personality=[],
                               project_id=u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f')


def test_check_all_resources():
    with mock.patch('fokia.provisioner_base.astakos'), \
         mock.patch('fokia.provisioner_base.KamakiConfig'), \
         mock.patch('fokia.provisioner_base.cyclades'), \
         mock.patch('fokia.provisioner_base.os.path.exists') as mock_exists:
        # Initilize Provisioner and mock some internal values
        mock_exists.return_value = True
        provisioner = Provisioner(None, "lambda")
        provisioner.astakos.get_projects.return_value = test_projects
        provisioner.astakos.get_quotas.return_value = test_quotas
        params = dict(project_id=u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f', cluster_size=3, vcpus=12,
                      ram=4096 * 3, disk=180, ip_allocation='all', network_request=1)
        # Call the check with sensible parameters to make sure it does not raise any exceptions
        provisioner.check_all_resources(test_quotas, **params)

        # Call the check function with arguments exceeding limits to make sure the correct
        # exception is called each time
        excessive_values = [({'cluster_size': 1000}, u'Cyclades VMs out of limit\n'),
                            ({'vcpus': 10 ** 10}, u'Cyclades cpu out of limit\n'),
                            ({'ram': 10 ** 10}, u'Cyclades ram out of limit\n'),
                            ({'disk': 10 ** 10}, u'Cyclades disk out of limit\n'),
                            ({'network_request': 30}, u'Private Network out of limit\n'), ]
        for extra_key, exception_message in excessive_values:
            with pytest.raises(ClientError) as ex:
                keys = params.copy()
                keys.update(extra_key)
                provisioner.check_all_resources(test_quotas, **keys)
            assert ex.value.message == exception_message


def test_create_vpn():
    with mock.patch('fokia.provisioner_base.astakos'), \
         mock.patch('fokia.provisioner_base.KamakiConfig'), \
         mock.patch('fokia.provisioner_base.cyclades') as cyclades, \
            mock.patch('fokia.provisioner_base.os.path.exists') as mock_exists:
        # Set up the mock objects
        mock_exists.return_value = True
        network_obj = cyclades.CycladesNetworkClient.return_value

        # Call the functions to set up a network
        provisioner = Provisioner(None, "lambda")
        provisioner.image_id = u'0ad78ab6-d3cd-42c9-8922-9cf63bbb7539'

        provisioner.network_client.create_network.return_value = test_ip
        provisioner.reserve_ip('6ff62e8e-0ce9-41f7-ad99-13a18ecada5f')
        provisioner.create_vpn('test_net_name', 'test_project_id')

        # Test that the network functions were called with the correct arguements
        network_obj.create_floatingip.assert_called_with(
            project_id='6ff62e8e-0ce9-41f7-ad99-13a18ecada5f')
        network_obj.create_network.assert_called_with(project_id='test_project_id',
                                                      type=network_obj.network_types[1],
                                                      name='test_net_name')


def test_create_vm():
    with mock.patch('fokia.provisioner_base.astakos') as astakos, \
            mock.patch('fokia.provisioner_base.KamakiConfig'), \
            mock.patch('fokia.provisioner_base.cyclades'), \
            mock.patch('fokia.provisioner_base.os.path.exists') as mock_exists:
        # Initialize the mocking objects
        mock_exists.return_value = True
        astakos.AstakosClient().get_projects().__getitem__().__getitem__.return_value = \
            'test_project_id'

        # Initilize the provisioner to be test
        provisioner = Provisioner(None, "lambda")

        # Mock some internat parameters
        provisioner.cyclades.create_server.return_value = test_vm
        provisioner.cyclades.list_images.return_value = [
            {'name': 'test_image_name', 'id': 'test_image_id', }]

        # Execute the function with some test parameters
        provisioner.create_vm(vm_name="test_name", flavor={'id': 'flavor_id'},
                              image_name='test_image_name')

        # Check that the correct arguements were used in the create server call
        provisioner.cyclades.create_server.assert_called_with(name='test_name',
                                                              image_id='test_image_id',
                                                              flavor_id='flavor_id',
                                                              project_id='test_project_id',
                                                              networks=[], personality=[])


def test_connect_vm():
    with mock.patch('fokia.provisioner_base.astakos'), \
         mock.patch('fokia.provisioner_base.KamakiConfig'), \
         mock.patch('fokia.provisioner_base.cyclades'), \
         mock.patch('fokia.provisioner_base.os.path.exists') as mock_exists:
        # Initialize Provisioner and mock some internal attributes
        mock_exists.return_value = True
        provisioner = Provisioner(None, "lambda")
        provisioner.network_client.create_port.return_value = True

        # Connect a vm to a network
        provisioner.connect_vm("test_vm_id", "test_net_id")

        # Test that the correct function
        provisioner.network_client.create_port.assert_called_with(network_id='test_net_id',
                                                                  device_id='test_vm_id')


def test_create_cluster():
    with mock.patch('fokia.provisioner_base.astakos'), \
         mock.patch('fokia.provisioner_base.KamakiConfig'), \
         mock.patch('fokia.provisioner_base.cyclades'), \
         mock.patch('fokia.provisioner.RSA') as rsa, \
         mock.patch('fokia.provisioner_base.os.path.exists') as mock_exists:
        # Initialize the provisioner and mock internal attributes concerning quotas
        mock_exists.return_value = True
        provisioner = Provisioner(None, "lambda")
        provisioner.astakos.get_projects.return_value = test_projects
        provisioner.astakos.get_quotas.return_value = test_quotas
        provisioner.cyclades.list_images.return_value = test_images
        provisioner.cyclades.list_flavors.return_value = test_flavors
        provisioner.network_client.create_floatingip().__getitem__.return_value = 'test_ip'
        provisioner.network_client.create_network().__getitem__.return_value = 'test_uuid'
        rsa.generate().exportKey.return_value = 'test_private_key'
        rsa.generate().publickey().exportKey.return_value = 'test_public_key'

        # Create cluster
        provisioner.create_lambda_cluster('test_master_name', slaves=2, vcpus_master=1,
                                          vcpus_slave=1, ram_master=1024, ram_slave=1024,
                                          disk_master=40, disk_slave=40, ip_allocation='all',
                                          network_request=1, project_name='test_project_name',
                                          extra_pub_keys='test_extra_pub_key')

        # Check that the astakos cyclades call gets the correct parameters
        assert provisioner.cyclades.create_server.call_args_list == [
            call(name='test_master_name', image_id=u'0ad78ab6-d3cd-42c9-8922-9cf63bbb7539',
                 flavor_id=3, project_id=u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f',
                 networks=[{u'fixed_ip': 'test_ip', u'uuid': 'test_ip'}, {u'uuid': 'test_uuid'}],
                 personality=[{
                     'owner': u'root', 'path': u'/root/.ssh/authorized_keys', 'group': u'root',
                     'mode': 384,
                     'contents': 'dGVzdF9leHRyYV9wdWJfa2V5CnRlc3RfcHVibGljX2tleSByb290'
                 }, {
                     'owner': u'root', 'path': u'/root/.ssh/id_rsa.pub', 'group': u'root',
                     'mode': 384, 'contents': 'dGVzdF9wdWJsaWNfa2V5IHJvb3Q='
                 }, {
                     'owner': u'root', 'path': u'/root/.ssh/id_rsa', 'group': u'root',
                     'mode': 384, 'contents': 'dGVzdF9wcml2YXRlX2tleQ=='
                 }]),
            call(name=u'lambda-node1', image_id=u'0ad78ab6-d3cd-42c9-8922-9cf63bbb7539',
                 flavor_id=3, project_id=u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f',
                 networks=[{u'fixed_ip': 'test_ip', u'uuid': 'test_ip'}, {u'uuid': 'test_uuid'}],
                 personality=[{
                     'owner': u'root', 'path': u'/root/.ssh/authorized_keys', 'group': u'root',
                     'mode': 384,
                     'contents': 'dGVzdF9leHRyYV9wdWJfa2V5CnRlc3RfcHVibGljX2tleSByb290'
                 }]),
            call(name=u'lambda-node2', image_id=u'0ad78ab6-d3cd-42c9-8922-9cf63bbb7539',
                 flavor_id=3, project_id=u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f',
                 networks=[{u'fixed_ip': 'test_ip', u'uuid': 'test_ip'}, {u'uuid': 'test_uuid'}],
                 personality=[{
                     'owner': u'root', 'path': u'/root/.ssh/authorized_keys', 'group': u'root',
                     'mode': 384,
                     'contents': 'dGVzdF9leHRyYV9wdWJfa2V5CnRlc3RfcHVibGljX2tleSByb290'
                 }])]


def test_misc_functions():
    with mock.patch('fokia.provisioner_base.astakos'), \
         mock.patch('fokia.provisioner_base.KamakiConfig'), \
         mock.patch('fokia.provisioner_base.cyclades'), \
         mock.patch('fokia.provisioner_base.os.path.exists') as mock_exists:
        # Initialize the provisioner and mock internal attributes concerning quotas

        mock_exists.return_value = True
        provisioner = Provisioner(None, "lambda")
        provisioner.astakos.get_projects.return_value = test_projects
        provisioner.astakos.get_quotas.return_value = test_quotas
        provisioner.cyclades.list_images.return_value = test_images
        provisioner.cyclades.list_flavors.return_value = test_flavors

        # Create a cluster and then destroy it to make all the fields required are initialized
        # correctly using the creation arguments

        provisioner.create_lambda_cluster('test_master_name', slaves=2, vcpus_master=1,
                                          vcpus_slave=1, ram_master=1024, ram_slave=1024,
                                          disk_master=40, disk_slave=40, ip_allocation='all',
                                          network_request=1, project_name='test_project_name',
                                          extra_pub_keys='test_extra_pub_key')
        provisioner.get_server_private_ip('12325')
        provisioner.get_cluster_details()
        provisioner.cyclades.delete_network("vpn_id_1")

        details = {"nodes": ["vm_id_1", "vm_id_2", "vm_id_3"], "vpn": "vpn_id_1", }
        provisioner.delete_lambda_cluster(details)

        # check the cyclades client got the correct ids to delete
        assert provisioner.cyclades.delete_server.call_args_list == [call('vm_id_1'),
                                                                     call('vm_id_2'),
                                                                     call('vm_id_3')]


if __name__ == "__main__":
    test_create_vpn()
    test_check_all_resources()
    test_create_vm()
    test_connect_vm()
    test_misc_functions()
    test_create_cluster()
