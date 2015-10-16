import mock

from fokia import utils


@mock.patch('fokia.utils.AstakosClient')
def test_get_user_okeanos_projects(mock_AstakosClient):
    # Define ~okeanos authentication url.
    authentication_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"
    # Define a fake ~okeanos token.
    authentication_token = "fake-token"

    # Set the responses of the mocks.
    mock_astakos_client = mock.Mock()

    mock_AstakosClient.return_value = mock_astakos_client

    mock_astakos_client.get_projects.return_value = [
        {'id': 1, 'name': "name1", 'garbage': 'garbage'},
        {'id': 2, 'name': "name2", 'garbage2': 'garbage2'}]

    # Make a call to get_user_okeanos_projects utils method.
    response = utils.get_user_okeanos_projects(authentication_url, authentication_token)

    # Assert that the proper mocks have been called.
    mock_AstakosClient.assert_called_with(authentication_url, authentication_token)

    mock_astakos_client.get_projects.assert_called_with()

    # Assert the contents of the response.
    assert response == [{'id': 1, 'name': "name1"}, {'id': 2, 'name': "name2"}]


@mock.patch('fokia.utils.CycladesComputeClient')
@mock.patch('fokia.utils.AstakosClient')
def test_get_vm_parameter_values(mock_AstakosClient, mock_CycladesComputeClient):
    # Define ~okeanos authentication url.
    authentication_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"
    # Define a fake ~okeanos token.
    authentication_token = "fake-token"

    # Set the responses of the mocks.
    cyclades_url = mock.Mock()
    mock_cyclades_compute_client = mock.Mock()
    mock_CycladesComputeClient.service_type = mock.Mock()
    mock_cyclades_compute_client.\
        list_flavors.return_value = [
            {
                u'SNF:allow_create': True,
                u'SNF:disk_template': u'drbd',
                u'SNF:volume_type': 1,
                u'disk': 20,
                u'id': 1,
                u'links': [{u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/1',
                            u'rel': u'self'},
                           {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/1',
                            u'rel': u'bookmark'}],
                u'name': u'C1R1024D20drbd',
                u'ram': 2048,
                u'vcpus': 2
            },
            {
                u'SNF:allow_create': True,
                u'SNF:disk_template': u'drbd',
                u'SNF:volume_type': 1,
                u'disk': 40,
                u'id': 3,
                u'links': [{u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                            u'rel': u'self'},
                           {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/3',
                             u'rel': u'bookmark'}],
                u'name': u'C1R1024D40drbd',
                u'ram': 1024,
                u'vcpus': 4
            },
            {
                u'SNF:allow_create': False,
                u'SNF:disk_template': u'drbd',
                u'SNF:volume_type': 1,
                u'disk': 80,
                u'id': 51,
                u'links': [{u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/51',
                            u'rel': u'self'},
                           {u'href': u'https://cyclades.okeanos.grnet.gr/compute/v2.0/flavors/51',
                            u'rel': u'bookmark'}],
                u'name': u'C1R512D80drbd',
                u'ram': 512,
                u'vcpus': 1
            }
        ]

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
