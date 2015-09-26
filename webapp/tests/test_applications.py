# coding=utf8
import uuid
import mock

from os import path

from rest_framework import status
from rest_framework.test import APITestCase

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from backend.models import User, Application
from backend.views import ApplicationViewSet
from backend.response_messages import ResponseMessages
from backend.exceptions import CustomParseError


class TestApplicationUpload(APITestCase):
    # Define ~okeanos authentication url.
    AUTHENTICATION_URL = "https://accounts.okeanos.grnet.gr/identity/v2.0"
    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    # A request to upload an application should include the following parameters:
    # description
    application_description = "Application description."
    # file
    application = SimpleUploadedFile("application.jar", "Hello World")
    # type
    application_type_batch = "batch"
    application_type_streaming = "streaming"
    # project_name
    project_name = "lambda.grnet.gr"

    def setUp(self):
        # Create a user and force authenticate.
        self.user = User.objects.create(uuid=uuid.uuid4())
        self.client.force_authenticate(user=self.user)

        # Add a fake token to every request authentication header to be used by the API.
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN))

        # Create an application on the database. It will be used to test the response of the API
        # when a request to upload an application with the same name is made.
        Application.objects.create(uuid=uuid.uuid4(), name="existing_application.jar",
                                   type=Application.BATCH)

    # Test for uploading an application when all the required information are provided.
    @mock.patch('backend.views.events.create_new_application')
    @mock.patch('backend.views.tasks.upload_application_to_pithos')
    def test_application_upload(self, mock_upload_application_to_pithos_task,
                                mock_create_new_application_event):

        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'file': self.application,
                                                   'type': self.application_type_batch,
                                                   'project_name': self.project_name})

        # Assert the structure of the response.
        self._assert_accepted_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_upload'])

        self.assertIsInstance(response.data['data'][0]['id'], uuid.UUID)

        self.assertRegexpMatches(response.data['data'][0]['links']['self'],
                                 r'^http://testserver/api/apps/([^/.]+)$')

        # Get the id of the uploaded application.
        application_id = response.data['data'][0]['id']

        # Assert that the proper tasks and views have been called.
        mock_create_new_application_event.delay.\
            assert_called_with(application_id, self.application.name,
                               ApplicationViewSet.pithos_container,
                               self.application_description, self.application_type_batch,
                               self.user)

        mock_upload_application_to_pithos_task.delay.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               ApplicationViewSet.pithos_container,
                               self.project_name,
                               path.join(settings.TEMPORARY_FILE_STORAGE, self.application.name),
                               application_id)

    # Test for uploading an application when all the required information are provided
    # but there is already an application with the same name uploaded.
    def test_existent_name(self):
        # file
        existing_application = SimpleUploadedFile("existing_application.jar", "Hello World")

        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'file': existing_application,
                                                   'type': self.application_type_batch,
                                                   'project_name': self.project_name})

        # Assert the structure of the response.
        self._assert_bad_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomParseError.messages['filename_already_exists_error'])

    # Test for uploading an application when no description is provided.
    @mock.patch('backend.views.events.create_new_application')
    @mock.patch('backend.views.tasks.upload_application_to_pithos')
    def test_no_description(self, mock_upload_application_to_pithos_task,
                            mock_create_new_application_event):
        response = self.client.post("/api/apps/", {'file': self.application,
                                                   'type': self.application_type_batch,
                                                   'project_name': self.project_name})

        # Assert the structure of the response.
        self._assert_accepted_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_upload'])

        self.assertIsInstance(response.data['data'][0]['id'], uuid.UUID)

        self.assertRegexpMatches(response.data['data'][0]['links']['self'],
                                 r'^http://testserver/api/apps/([^/.]+)$')

        # Get the id of the uploaded application.
        application_id = response.data['data'][0]['id']

        # Assert that the proper tasks and views have been called.
        mock_create_new_application_event.delay.\
            assert_called_with(application_id, self.application.name,
                               ApplicationViewSet.pithos_container, "",
                               self.application_type_batch, self.user)

        mock_upload_application_to_pithos_task.delay.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               ApplicationViewSet.pithos_container,
                               self.project_name,
                               path.join(settings.TEMPORARY_FILE_STORAGE, self.application.name),
                               application_id)

    # Test for uploading an application when no file is provided.
    def test_no_file(self):
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'type': self.application_type_batch,
                                                   'project_name': self.project_name})

        # Assert the structure of the response.
        self._assert_bad_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'], CustomParseError.
                                                               messages['no_file_error'])

    # Test for uploading an application with type "streaming".
    @mock.patch('backend.views.events.create_new_application')
    @mock.patch('backend.views.tasks.upload_application_to_pithos')
    def test_type_streaming(self, mock_upload_application_to_pithos_task,
                            mock_create_new_application_event):

        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'file': self.application,
                                                   'type': self.application_type_streaming,
                                                   'project_name': self.project_name})

        # Assert the structure of the response.
        self._assert_accepted_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_upload'])

        self.assertIsInstance(response.data['data'][0]['id'], uuid.UUID)

        self.assertRegexpMatches(response.data['data'][0]['links']['self'],
                                 r'^http://testserver/api/apps/([^/.]+)$')

        # Get the id of the uploaded application.
        application_id = response.data['data'][0]['id']

        # Assert that the proper tasks and views have been called.
        mock_create_new_application_event.delay.\
            assert_called_with(application_id, self.application.name,
                               ApplicationViewSet.pithos_container,
                               self.application_description, self.application_type_streaming,
                               self.user)

        mock_upload_application_to_pithos_task.delay.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               ApplicationViewSet.pithos_container,
                               self.project_name,
                               path.join(settings.TEMPORARY_FILE_STORAGE, self.application.name),
                               application_id)

    # Test for uploading an application when no type is provided.
    def test_no_type(self):
        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'file': self.application,
                                                   'project_name': self.project_name})

        # Assert the structure of the response.
        self._assert_bad_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'], CustomParseError.
                                                               messages['no_type_error'])

    # Test for uploading an application when a wrong type is provided.
    def test_wrong_type(self):
        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'file': self.application,
                                                   'type': "a-wrong-type",
                                                   'project_name': self.project_name})

        # Assert the structure of the response.
        self._assert_bad_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'], CustomParseError.
                                                               messages['no_type_error'])

    # Test for uploading an application when no project name is provided.
    @mock.patch('backend.views.events.create_new_application')
    @mock.patch('backend.views.tasks.upload_application_to_pithos')
    def test_no_project_name(self, mock_upload_application_to_pithos_task,
                             mock_create_new_application_event):

        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'file': self.application,
                                                   'type': self.application_type_batch})

        # Assert the structure of the response.
        self._assert_accepted_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_upload'])

        self.assertIsInstance(response.data['data'][0]['id'], uuid.UUID)

        self.assertRegexpMatches(response.data['data'][0]['links']['self'],
                                 r'^http://testserver/api/apps/([^/.]+)$')

        # Get the id of the uploaded application.
        application_id = response.data['data'][0]['id']

        # Assert that the proper tasks and views have been called.
        mock_create_new_application_event.delay.\
            assert_called_with(application_id, self.application.name,
                               ApplicationViewSet.pithos_container,
                               self.application_description, self.application_type_batch,
                               self.user)

        mock_upload_application_to_pithos_task.delay.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               ApplicationViewSet.pithos_container, "",
                               path.join(settings.TEMPORARY_FILE_STORAGE, self.application.name),
                               application_id)

    def _assert_accepted_response_structure(self, response):
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

    def _assert_bad_request_response_structure(self, response):
        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)
