# coding=utf8
import uuid
import mock

from os import path

from rest_framework import status
from rest_framework.test import APITestCase

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from backend.models import User
from backend.views import ApplicationViewSet
from backend.response_messages import ResponseMessages

class TestApplication(APITestCase):
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

    def _assert_accepted_response(self, response):
        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        self.assertGreater(len(response.data['data']), 0)
        self.assertIn('id', response.data['data'][0])
        self.assertIn('links', response.data['data'][0])

        self.assertIn('self', response.data['data'][0]['links'])

    # Test for uploading an application.
    @mock.patch('backend.views.events.create_new_application')
    @mock.patch('backend.views.tasks.upload_application_to_pithos')
    def test_application_upload(self, mock_upload_application_to_pithos_task,
                                mock_create_new_application_event):
        # A request to upload an application should include the following parameters:
        # description
        application_description = "Application description."
        # file
        application = SimpleUploadedFile("application.jar", "Hello World")
        # type
        application_type = "batch"
        # project_name
        project_name = "lambda.grnet.gr"

        # Create an application file.

        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': application_description,
                                                   'file': application,
                                                   'type': application_type,
                                                   'project_name': project_name})

        # Assert the structure of the response
        self._assert_accepted_response(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_upload'])

        self.assertIsInstance(response.data['data'][0]['id'], uuid.UUID)

        self.assertRegexpMatches(response.data['data'][0]['links']['self'],
                                 r'^http://testserver/api/apps/([^/.]+)$')

        application_id = response.data['data'][0]['id']

        mock_create_new_application_event.delay.\
            assert_called_with(application_id, application.name,
                               ApplicationViewSet.pithos_container,
                               application_description, application_type, self.user)

        mock_upload_application_to_pithos_task.delay.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               ApplicationViewSet.pithos_container,
                               project_name,
                               path.join(settings.TEMPORARY_FILE_STORAGE, application.name),
                               application_id)
