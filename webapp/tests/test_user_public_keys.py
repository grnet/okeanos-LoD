import uuid
import mock

from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import User
from backend.response_messages import ResponseMessages


class TestUserPublicKeys(APITestCase):
    """
    Contains tests for user public keys API calls.
    """

    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    class CycladesResponse:
        """
        Class that emulates a cyclades response object.
        """

        def __init__(self, content=None):
            self.content = content

    def setUp(self):
        # Create a user and force authenticate.
        self.user = User.objects.create(uuid=uuid.uuid4())
        self.client.force_authenticate(user=self.user)

        # Add a fake token to every request authentication header to be used by the API.
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN))

    # Test for getting the public keys stored on ~okeanos.
    @mock.patch('backend.authenticate_user.requests.get')
    def test_user_public_keys(self, mock_requests_get):

        # Determine the response of the mock.
        mock_requests_get.return_value = self.CycladesResponse('[{"value_1": "value_1"},\
                                                                 {"value_2": "value_2"},\
                                                                 {"value_N": "value_N"}]')

        # Make a request to get the public keys stored on ~okeanos.
        response = self.client.get("/api/user-public-keys/")

        # Assert the response status code.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the structure of the response.
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['user_public_keys'])

        self.assertEqual(response.data['data'], [{"value_1": "value_1"},
                                                 {"value_2": "value_2"},
                                                 {"value_N": "value_N"}])
