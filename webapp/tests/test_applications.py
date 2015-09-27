# coding=utf8
import uuid
import mock

from os import path

from random import randint

from rest_framework import status
from rest_framework.test import APITestCase

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from backend.models import User, Application
from backend.views import ApplicationViewSet
from backend.response_messages import ResponseMessages
from backend.exceptions import CustomParseError, CustomNotFoundError


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

        self.assertEqual(len(response.data['data']), 1)
        self.assertIn('id', response.data['data'][0])
        self.assertIn('links', response.data['data'][0])

        self.assertIn('self', response.data['data'][0]['links'])

    def _assert_bad_request_response_structure(self, response):
        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)


class TestApplicationsList(APITestCase):
    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    def setUp(self):
        # Create a user and force authenticate.
        self.user = User.objects.create(uuid=uuid.uuid4())
        self.client.force_authenticate(user=self.user)

        # Add a fake token to every request authentication header to be used by the API.
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN))

    # Test for listing the existing applications.
    def test_applications_list(self):
        # Create some applications on the database.
        number_of_applications = randint(0, 100)
        for i in range(number_of_applications):
            Application.objects.create(uuid=uuid.uuid4(), name="application_{i}.jar".format(i=i),
                                       type=Application.BATCH)

        # Make a request to list the existing applications.
        response = self.client.get("/api/apps/")

        # Assert the structure of the response.
        self._assert_success_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(len(response.data['data']), number_of_applications)

        self._assert_success_request_response_content(response)

    # Test for listing existing applications when there is no application uploaded.
    def test_applications_list_empty(self):
        # Make a request to list the existing applications.
        response = self.client.get("/api/apps/")

        # Assert the structure of the response.
        self._assert_success_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(len(response.data['data']), 0)

        self._assert_success_request_response_content(response)

    # Test for listing existing applications using pagination.
    def test_applications_list_pagination(self):
        # Create some applications on the database.
        number_of_applications = randint(0, 100)
        for i in range(number_of_applications):
            Application.objects.create(uuid=uuid.uuid4(), name="application_{i}.jar".format(i=i),
                                       type=Application.BATCH)

        # Make a request using both limit and offset parameters.
        limit = randint(0, 100)
        offset = randint(-100, 100)
        response = self.client.get("/api/apps/?limit={limit}&offset={offset}".
                                   format(limit=limit, offset=offset))

        # Assert the structure of the response.
        self._assert_success_request_response_structure(response)

        self.assertIn('pagination', response.data)

        # Assert the contents of the response.
        number_of_expected_applications = None
        if offset < 0:
            number_of_expected_applications = number_of_applications
        elif offset < number_of_applications:
            number_of_expected_applications = number_of_applications - offset
        else:
            number_of_expected_applications = 0

        if number_of_expected_applications >= limit:
            self.assertEqual(len(response.data['data']), limit)
        else:
            self.assertEqual(len(response.data['data']), number_of_expected_applications)

        if offset >= 0:
            self._assert_success_request_response_content(response, offset)
        else:
            self._assert_success_request_response_content(response)

    # Test for listing existing applications when limit value for pagination is negative.
    def test_negative_pagination_limit(self):
        # Make a request.
        limit = randint(-100, -1)
        response = self.client.get("/api/apps/?limit={limit}".format(limit=limit))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'], CustomParseError.
                                                               messages['limit_value_error'])

    def _assert_success_request_response_structure(self, response):
        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the structure of the response.
        self.assertIn('status', response.data)
        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])

        self.assertIn('data', response.data)
        for application in response.data['data']:
            self.assertIn('id', application)
            self.assertIn('name', application)

    def _assert_success_request_response_content(self, response, offset=0):
        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['applications_list'])

        for index, application in enumerate(response.data['data']):
            self.assertEqual(application['name'], "application_{index}.jar".
                             format(index=index + offset))
            self.assertRegexpMatches(application['id'], r'^([^/.]+)$')


class TestApplicationDetails(APITestCase):
    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    def setUp(self):
        # Create a user and force authenticate.
        self.user = User.objects.create(uuid=uuid.uuid4())
        self.client.force_authenticate(user=self.user)

        # Add a fake token to every request authentication header to be used by the API.
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN))
        # Create a uuid.
        self.random_uuid = uuid.uuid4()

        # Save an application on the database with the specified uuid.
        Application.objects.create(uuid=self.random_uuid, name="application.jar",
                                   description="A description.", type=Application.BATCH)

    # Test for getting the details of an application.
    def test_application_details(self):
        # Make a request to get the details of the specified application.
        response = self.client.get("/api/apps/{random_uuid}/".format(random_uuid=self.random_uuid))

        # Assert the structure of the response.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('status', response.data)
        self.assertIn('data', response.data)

        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])

        self.assertEqual(len(response.data['data']), 1)

        self.assertIn('id', response.data['data'][0])
        self.assertIn('name', response.data['data'][0])
        self.assertIn('path', response.data['data'][0])
        self.assertIn('type', response.data['data'][0])
        self.assertIn('description', response.data['data'][0])
        self.assertIn('connections', response.data['data'][0])
        self.assertIn('status', response.data['data'][0])

        self.assertIn('message', response.data['data'][0]['status'])
        self.assertIn('code', response.data['data'][0]['status'])
        self.assertIn('detail', response.data['data'][0]['status'])

        # Assert the content of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_details'])

        self.assertEqual(response.data['data'][0]['id'],
                         "{random_uuid}".format(random_uuid=self.random_uuid))
        self.assertEqual(response.data['data'][0]['name'], "application.jar")
        self.assertEqual(response.data['data'][0]['path'], "lambda_applications")
        self.assertEqual(response.data['data'][0]['type'], "BATCH")
        self.assertEqual(response.data['data'][0]['description'], "A description.")
        self.assertEqual(len(response.data['data'][0]['connections']), 0)

        self.assertEqual(response.data['data'][0]['status']['message'], "UPLOADING")
        self.assertEqual(response.data['data'][0]['status']['code'], "1")
        self.assertEqual(response.data['data'][0]['status']['detail'],
                         ResponseMessages.application_status_details[
                             response.data['data'][0]['status']['message']])

    # Test for requesting the details of an application that doesn't exist.
    def test_non_existent_id(self):
        # Make a request to get the details of the specified application.
        response = self.client.get("/api/apps/{random_uuid}/".format(random_uuid=uuid.uuid4()))

        # Assert the structure of the response.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the content of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['application_not_found'])
