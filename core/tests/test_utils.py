import mock

from fokia import utils


@mock.patch('fokia.utils.AstakosClient')
def test_get_user_okeanos_projects(mock_astakos_client):
    # Define ~okeanos authentication url.
    AUTHENTICATION_URL = "https://accounts.okeanos.grnet.gr/identity/v2.0"
    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    # Set the responses of the mocks.
    mock_astakos_client.get_projects.return_value = [
        {'id': 1, 'name': "name1", 'garbage': 'garbage'},
        {'id': 2, 'name': "name2", 'garbage2': 'garbage2'}]

    # Make a call to get_user_okeanos_projects utils method.
    response = utils.get_user_okeanos_projects(AUTHENTICATION_URL, AUTHENTICATION_TOKEN)

    # Assert that the proper mocks have been called.
    mock_astakos_client.assert_called_with(AUTHENTICATION_URL, AUTHENTICATION_TOKEN)

    mock_astakos_client.get_projects.assert_called_with()

    # Assert the contents of the response.
    assert response == [{'id': 1, 'name': "name1"}, {'id': 2, 'name': "name2"}]
