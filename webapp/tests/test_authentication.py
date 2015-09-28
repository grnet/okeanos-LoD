from rest_framework import status
from rest_framework.test import APITestCase

from backend.exceptions import CustomAuthenticationFailed

class TestAuthentication(APITestCase):
    """
    Contains tests for authentication API calls.
    """

    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    def setUp(self):

        # Add a fake token to every request authentication header to be used by the API.
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN))

    # Test for making a request with an invalid token.
    def test_invalid_token(self):

        # Make a request with an invalid token.
        response = self.client.get("/api/lambda-instances/")

        # Assert the status code of the response.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomAuthenticationFailed.default_detail)
