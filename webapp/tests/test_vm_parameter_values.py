import mock
import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import User
from backend.response_messages import ResponseMessages


class TestVMParameterValues(APITestCase):
    """
    Contains tests for vm parameter values API call.
    """

    # Define ~okeanos authentication url.
    AUTHENTICATION_URL = "https://accounts.okeanos.grnet.gr/identity/v2.0"
    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    def setUp(self):
        # Create a user and force authenticate.
        self.user = User.objects.create(uuid=uuid.uuid4())
        self.client.force_authenticate(user=self.user)

        # Add a fake token to every request authentication header to be used by the API.
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN))

    # Test for getting vm parameter values.
    @mock.patch('backend.views.get_vm_parameter_values', return_value={
        "disk": [5, 10, 20, 40, 60],
        "vcpus": [1, 2, 4, 8],
        "ram": [512, 1024, 2048, 4096, 6144, 8192]
    })
    def test_vm_parameter_values(self, mock_get_vm_parameter_values):
        # Make a request to get the vm parameter values.
        response = self.client.get("/api/vm-parameter-values/")

        # Assert that the proper mocks have been called.
        mock_get_vm_parameter_values.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN)

        # Assert the structure of the response.
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['vm_parameter_values'])

        self.assertEqual(response.data['data'], [{
            "disk": [5, 10, 20, 40, 60],
            "vcpus": [1, 2, 4, 8],
            "ram": [512, 1024, 2048, 4096, 6144, 8192]
        }])
