import mock
import pytest
from mock import patch, call, MagicMock
from fokia import utils
from kamaki.clients import ClientError


@patch('fokia.utils.AstakosClient')
def test_get_user_okeanos_projects(mock_AstakosClient):
    # Define ~okeanos authentication url.
    authentication_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"
    # Define a fake ~okeanos token.
    authentication_token = "fake-token"

    # Set the responses of the mocks.
    mock_astakos_client = mock.Mock()

    mock_AstakosClient.return_value = mock_astakos_client

    mock_astakos_client.get_projects.return_value = [
        {'id': '1', 'name': "name1", 'state': 'active', 'garbage': 'garbage'},
        {'id': '2', 'name': "name2", 'state': 'active', 'garbage2': 'garbage2'},
        {'id': '3', 'name': "name3", 'state': 'deleted', 'garbage3': 'garbage3'}]

    mock_astakos_client.get_quotas.return_value = {
        '1': {
            u'astakos.pending_app': {
                u'limit': 0,
                u'pending': 0,
                u'project_limit': 0,
                u'project_pending': 0,
                u'project_usage': 0,
                u'usage': 0
            },
            u'cyclades.cpu': {
                u'limit': 20,
                u'pending': 0,
                u'project_limit': 100,
                u'project_pending': 0,
                u'project_usage': 95,
                u'usage': 4
            },
            u'cyclades.disk': {
                u'limit': 200,
                u'pending': 0,
                u'project_limit': 1000,
                u'project_pending': 0,
                u'project_usage': 150,
                u'usage': 150
            },
            u'cyclades.floating_ip': {
                u'limit': 5,
                u'pending': 0,
                u'project_limit': 30,
                u'project_pending': 0,
                u'project_usage': 26,
                u'usage': 4
            },
            u'cyclades.network.private': {
                u'limit': 50,
                u'pending': 0,
                u'project_limit': 50,
                u'project_pending': 0,
                u'project_usage': 40,
                u'usage': 49
            },
            u'cyclades.ram': {
                u'limit': 100,
                u'pending': 0,
                u'project_limit': 1000,
                u'project_pending': 0,
                u'project_usage': 400,
                u'usage': 50
            },
            u'cyclades.vm': {
                u'limit': 1000,
                u'pending': 0,
                u'project_limit': 10000,
                u'project_pending': 0,
                u'project_usage': 9999,
                u'usage': 0
            },
            u'pithos.diskspace': {
                u'limit': 1000,
                u'pending': 0,
                u'project_limit': 1000,
                u'project_pending': 0,
                u'project_usage': 50,
                u'usage': 0
            }
        },
        '2': {
            u'astakos.pending_app': {
                u'limit': 0,
                u'pending': 0,
                u'project_limit': 0,
                u'project_pending': 0,
                u'project_usage': 0,
                u'usage': 0
            },
            u'cyclades.cpu': {
                u'limit': 1,
                u'pending': 0,
                u'project_limit': 100,
                u'project_pending': 0,
                u'project_usage': 75,
                u'usage': 1
            },
            u'cyclades.disk': {
                u'limit': 200,
                u'pending': 0,
                u'project_limit': 200,
                u'project_pending': 0,
                u'project_usage': 200,
                u'usage': 10
            },
            u'cyclades.floating_ip': {
                u'limit': 0,
                u'pending': 0,
                u'project_limit': 100,
                u'project_pending': 0,
                u'project_usage': 25,
                u'usage': 0
            },
            u'cyclades.network.private': {
                u'limit': 100,
                u'pending': 0,
                u'project_limit': 100,
                u'project_pending': 0,
                u'project_usage': 100,
                u'usage': 0
            },
            u'cyclades.ram': {
                u'limit': 0,
                u'pending': 0,
                u'project_limit': 500,
                u'project_pending': 0,
                u'project_usage': 0,
                u'usage': 0
            },
            u'cyclades.vm': {
                u'limit': 100,
                u'pending': 0,
                u'project_limit': 100,
                u'project_pending': 0,
                u'project_usage': 20,
                u'usage': 21
            },
            u'pithos.diskspace': {
                u'limit': 0,
                u'pending': 0,
                u'project_limit': 0,
                u'project_pending': 0,
                u'project_usage': 0,
                u'usage': 0
            }
        },
    }

    # Make a call to get_user_okeanos_projects utils method.
    response = utils.get_user_okeanos_projects(authentication_url, authentication_token)

    # Assert that the proper mocks have been called.
    mock_AstakosClient.assert_called_with(authentication_url, authentication_token)

    mock_astakos_client.get_projects.assert_called_with()
    mock_astakos_client.get_quotas.assert_called_with()

    # Assert the contents of the response.
    assert response == [
        {
            'id': '1',
            'name': "name1",
            'vm': 1,
            'cpu': 5,
            'ram': 50,
            'disk': 50,
            'floating_ip': 1,
            'private_network': 1,
            'pithos_space': 950
        },
        {
            'id': '2',
            'name': "name2",
            'vm': 79,
            'cpu': 0,
            'ram': 0,
            'disk': 0,
            'floating_ip': 0,
            'private_network': 0,
            'pithos_space': 0
        }]


@patch('fokia.utils.CycladesComputeClient')
@patch('fokia.utils.AstakosClient')
def test_get_vm_parameter_values(mock_AstakosClient, mock_CycladesComputeClient):
    # Define ~okeanos authentication url.
    authentication_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"
    # Define a fake ~okeanos token.
    authentication_token = "fake-token"

    # Set the responses of the mocks.
    cyclades_url = mock.Mock()
    mock_cyclades_compute_client = mock.Mock()
    mock_CycladesComputeClient.service_type = mock.Mock()
    mock_cyclades_compute_client.list_flavors.return_value = [{
        u'SNF:allow_create': True, u'SNF:disk_template': u'drbd', u'SNF:volume_type': 1,
        u'disk':             20, u'id': 1, u'links': [{
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/1', u'rel': u'self'
        }, {
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/1',
            u'rel':  u'bookmark'
        }], u'name':         u'C1R1024D20drbd', u'ram': 2048, u'vcpus': 2
    }, {
        u'SNF:allow_create': True, u'SNF:disk_template': u'drbd', u'SNF:volume_type': 1,
        u'disk':             40, u'id': 3, u'links': [{
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3', u'rel': u'self'
        }, {
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
            u'rel':  u'bookmark'
        }], u'name':         u'C1R1024D40drbd', u'ram': 1024, u'vcpus': 4
    }, {
        u'SNF:allow_create': False, u'SNF:disk_template': u'drbd', u'SNF:volume_type': 1,
        u'disk':             80, u'id': 51, u'links': [{
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/51', u'rel': u'self'
        }, {
            u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/51',
            u'rel':  u'bookmark'
        }], u'name':         u'C1R512D80drbd', u'ram': 512, u'vcpus': 1
    }]

    mock_CycladesComputeClient.return_value = mock_cyclades_compute_client

    mock_astakos_client = mock.Mock()
    mock_astakos_client.get_endpoint_url.return_value = cyclades_url
    mock_AstakosClient.return_value = mock_astakos_client

    # Make a call to get vm parameter values method.
    response = utils.get_vm_parameter_values(authentication_url, authentication_token)

    # Assert that the proper mocks have been called.
    mock_AstakosClient.assert_called_with(authentication_url, authentication_token)
    mock_astakos_client.get_endpoint_url.assert_called_with(mock_CycladesComputeClient.service_type)
    mock_CycladesComputeClient.assert_called_with(cyclades_url, authentication_token)
    mock_cyclades_compute_client.list_flavors.assert_called_with(detail=True)

    # Assert the contents of the response
    assert response == {'vcpus': [2, 4], 'ram': [1024, 2048], 'disk': [20, 40]}


@patch('fokia.utils.os')
@patch('fokia.utils.CycladesComputeClient')
@patch('fokia.utils.AstakosClient')
@patch('fokia.utils.PithosClient')
def test_lambda_instance_start_stop(pithosclient, astakosclient, cycladesclient, mock_os):
    url, token = "test_auth_url", "test_auth_token"
    master_id = "test_master_id"
    slave_ids = ["test_slave_id_1", "test_slave_id_2", "test_slave_id_3"]
    utils.lambda_instance_start(url, token, master_id, slave_ids)
    utils.lambda_instance_stop(url, token, master_id, slave_ids)
    assert cycladesclient.return_value.start_server.call_args_list == [call('test_slave_id_1'),
                                                                       call('test_slave_id_2'),
                                                                       call('test_slave_id_3'),
                                                                       call('test_master_id')]
    assert cycladesclient.return_value.shutdown_server.call_args_list == [call('test_master_id'),
                                                                          call('test_slave_id_1'),
                                                                          call('test_slave_id_2'),
                                                                          call('test_slave_id_3')]


@patch('fokia.utils.os')
@patch('fokia.utils.CycladesComputeClient')
@patch('fokia.utils.AstakosClient')
@patch('fokia.utils.PithosClient')
def test_check_user_token(pithosclient, astakosclient, cycladesclient, mock_os):
    url, token = "test_auth_url", "test_auth_token"
    user_info = MagicMock()
    astakosclient.return_value.authenticate.side_effect = [ClientError('UNAUTHORIZED'), user_info]
    with pytest.raises(ClientError):
        res = utils.check_auth_token(token, url)
        assert res[0] is False
    res = utils.check_auth_token(token, url)
    assert res[0] is True
    assert res[1] == user_info


@patch('fokia.utils.os')
@patch('fokia.utils.CycladesComputeClient')
@patch('fokia.utils.AstakosClient')
@patch('fokia.utils.PithosClient')
def test_pithos_file_handling(mock_pithos, astakosclient, cycladesclient, mock_os):
    url, token = "test_auth_url", "test_auth_token"
    container, filename = "test_container_name", "test_filename"
    file_obj = mock.Mock()
    pithosclient = mock_pithos.return_value
    mock_os.path.basename.return_value = "test_file_name"
    utils.upload_file_to_pithos(url, token, container, "test_project_id", file_obj)
    utils.download_file_from_pithos(url, token, container, filename, "test_destination")
    utils.delete_file_from_pithos(url, token, container, filename)
    pithosclient.upload_object.assert_called_with('test_file_name', file_obj)
    pithosclient.download_object.assert_called_with('test_filename', 'test_destination')
    pithosclient.delete_object.assert_called_with('test_filename')


if __name__ == '__main__':
    test_lambda_instance_start_stop()
    test_check_user_token()
    test_pithos_file_handling()
