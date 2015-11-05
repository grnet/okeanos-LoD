from mock import patch, MagicMock, call

from fokia.lambda_instance_manager import lambda_instance_destroy, create_cluster

test_flavors = [{
    u'SNF:allow_create': True, u'SNF:disk_template': u'drbd', u'SNF:volume_type': 1, u'disk': 20,
    u'id': 1, u'links': [{
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/1', u'rel': u'self'
    }, {
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/1', u'rel': u'bookmark'
    }], u'name': u'C1R1024D20drbd', u'ram': 1024, u'vcpus': 1
}, {
    u'SNF:allow_create': True, u'SNF:disk_template': u'drbd', u'SNF:volume_type': 1, u'disk': 40,
    u'id': 3, u'links': [{
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3', u'rel': u'self'
    }, {
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3', u'rel': u'bookmark'
    }], u'name': u'C1R1024D40drbd', u'ram': 1024, u'vcpus': 1
}, {
    u'SNF:allow_create': True, u'SNF:disk_template': u'drbd', u'SNF:volume_type': 1, u'disk': 20,
    u'id': 4, u'links': [{
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/4', u'rel': u'self'
    }, {
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/4', u'rel': u'bookmark'
    }], u'name': u'C1R2048D20drbd', u'ram': 2048, u'vcpus': 1
}]

test_images = [{
    u'created': u'2015-06-26T11:29:59+00:00', u'id': u'0035ac89-a86e-4108-93e8-93e294b74a3d',
    u'is_snapshot': False, u'links': [{
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/1232', u'rel': u'self'
    }, {
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/234d', u'rel': u'bookmark'
    }, {
        u'href': u'https://cyclades.okeanos.grnet.gr/image/v1.0/images/345', u'rel': u'alternate'
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
    u'created': u'2014-03-11T12:55:07+00:00', u'id': u'0099593e-4f6d-48bf-8f03-0cec7fabb05b',
    u'is_snapshot': False, u'links': [{
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/123', u'rel': u'self'
    }, {
        u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/images/2345', u'rel': u'bookmark'
    }, {
        u'href': u'https://cyclades.okeanos.grnet.gr/image/v1.0/images/3456', u'rel': u'alternate'
    }], u'metadata': {
        u'description': u'Master clone', u'os': u'ubuntu', u'osfamily': u'linux',
        u'partition_table': u'msdos', u'root_partition': u'1', u'users': u'user hduser'
    }, u'name': u'master_clone', u'progress': 100, u'public': True, u'status': u'ACTIVE',
    u'tenant_id': u'607bc20e-ae01-46ca-8a7d-d37b92e9908f',
    u'updated': u'2014-03-11T12:55:07+00:00',
    u'user_id': u'607bc20e-ae01-46ca-8a7d-d37b92e9908f'
}]

test_projects = [{
    u'creation_date': u'2015-06-09T09:46:44.327826+00:00', u'description': u'',
    u'end_date': u'2015-11-30T00:00:00+00:00', u'homepage': u'',
    u'id': u'6ff62e8e-0ce9-41f7-ad99-13a18ecada5f', u'join_policy': u'moderated',
    u'leave_policy': u'auto', u'max_members': 9223372036854775807, u'name': u'lambda.grnet.gr',
    u'owner': u'69c6686c-4e3e-407e-96b4-c21ef7d5def5', u'private': False, u'resources': {
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
            'project_limit': 10, 'project_pending': 0, 'project_usage': 7, 'usage': 0, 'limit': 4,
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
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/'
                     u'v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
            u'rel': u'self'
        }, {
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/'
                     u'v2.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
            u'rel': u'bookmark'
        }, {
            u'href': u'https://cyclades.okeanos.grnet.gr/image/'
                     u'v1.0/images/0e399015-8723-4c78-8198-75bdf693cdde',
            u'rel': u'alternate'
        }]
    }, u'suspended': False, u'flavor': {
        u'id': 3, u'links': [{
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3', u'rel': u'self'
        }, {
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


def test_create_cluster():
    with patch('fokia.lambda_instance_manager.Provisioner') as provisioner, \
            patch('fokia.lambda_instance_manager.Manager'), \
            patch('fokia.lambda_instance_manager.Storm'), \
            patch('fokia.lambda_instance_manager.open', create=True) as mock_open, \
            patch('fokia.lambda_instance_manager.os'):
        # initialize mock with builtin file as spec
        mock_open.return_value = MagicMock(spec=file)

        # create a new cluster given an id
        create_cluster('test_cluster_id', master_image_id="9819231a-e9e2-40f7-93f1-e2e4cb50cc33",
                       slave_image_id="9819231a-e9e2-40f7-93f1-e2e4cb50cc33")

        # check from mocked objects that the creation function was called with the
        # intended arguements
        provisioner_obj = provisioner.return_value
        provisioner_obj.create_lambda_cluster. \
            assert_called_with(vm_name='lambda-master',
                               project_name='lambda.grnet.gr',
                               extra_pub_keys=None,
                               vcpus_master=4, network_request=1,
                               disk_slave=40, slaves=1,
                               ram_slave=4096, ram_master=4096,
                               vcpus_slave=4,
                               master_image_id="9819231a-e9e2-40f7-93f1-e2e4cb50cc33",
                               slave_image_id="9819231a-e9e2-40f7-93f1-e2e4cb50cc33",
                               ip_allocation='master',
                               disk_master=40)


def test_destroy_cluster():
    with patch('fokia.lambda_instance_manager.Provisioner') as provisioner, \
            patch('fokia.lambda_instance_manager.Manager'), \
            patch('fokia.lambda_instance_manager.Storm') as storm, \
            patch('fokia.lambda_instance_manager.open', create=True) as mock_open, \
            patch('fokia.lambda_instance_manager.os'):
        # Initialize mocks to be used
        mock_open.return_value = MagicMock(spec=file)
        provisioner_obj = provisioner.return_value
        cyclades_compute = provisioner_obj.cyclades
        cyclades_network = provisioner_obj.network_client

        # Execute instance destroy with test values
        lambda_instance_destroy('test_cluster_id', 'test_token', 'master_id',
                                ['slave_id_1', 'slave_id_2'], 'test_public_ip',
                                'test_private_net_id')

        # make sure all server ids are called to be deleted
        assert cyclades_compute.delete_server.call_args_list == [call('master_id'),
                                                                 call('slave_id_1'),
                                                                 call('slave_id_2'),
                                                                 ]

        # make sure all network ips and vpns are deleted
        cyclades_network.delete_floatingip.assert_called_with('test_public_ip')
        cyclades_network.delete_network.assert_called_with('test_private_net_id')

        # make sure private keys created for the specific server are deleted
        assert storm.return_value.delete_entry.call_args_list == [
            call('snf-master_id.vm.okeanos.grnet.gr'),
            call('snf-slave_id_1.local'),
            call('snf-slave_id_2.local'),
        ]


if __name__ == '__main__':
    test_create_cluster()
    test_destroy_cluster()
