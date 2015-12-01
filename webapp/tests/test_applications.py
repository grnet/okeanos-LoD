import uuid
import mock

from os import path

from random import randint

from rest_framework import status
from rest_framework.test import APITestCase

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from backend.models import User, Application, LambdaInstance, LambdaInstanceApplicationConnection
from backend.views import ApplicationViewSet
from backend.response_messages import ResponseMessages
from backend.exceptions import CustomParseError, CustomNotFoundError, CustomCantDoError,\
    CustomAlreadyDoneError


class TestApplicationUpload(APITestCase):
    """
    Contains tests for application upload API call.
    """

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
    # execution_environment_name
    execution_environment_name = "Stream"

    user_projects = [
        {'name': "lambda.grnet.gr", 'id': uuid.uuid4()},
        {'name': "project_1", 'id': uuid.uuid4()},
        {'name': "project_2", 'id': uuid.uuid4()},
        {'name': "project_3", 'id': uuid.uuid4()},
        {'name': "project_4", 'id': uuid.uuid4()}
    ]

    def setUp(self):
        # Create a user and force authenticate.
        self.user = User.objects.create(uuid=uuid.uuid4())
        self.client.force_authenticate(user=self.user)

        # Add a fake token to every request authentication header to be used by the API.
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN))

    # Test for uploading an application.
    @mock.patch('backend.views.get_user_okeanos_projects')
    @mock.patch('backend.views.events.create_new_application')
    @mock.patch('backend.views.tasks.upload_application_to_pithos')
    def test_application_upload(self, mock_upload_application_to_pithos_task,
                                mock_create_new_application_event,
                                mock_get_user_okeanos_projects):
        # Configure return values for mocks.
        chosen_project = self.user_projects[0]
        mock_get_user_okeanos_projects.return_value = self.user_projects

        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'file': self.application,
                                                   'type': self.application_type_batch,
                                                   'project_name': self.project_name,
                                                   'execution_environment_name':
                                                   self.execution_environment_name})

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
            assert_called_with(application_id, self.application.name, chosen_project['id'],
                               ApplicationViewSet.pithos_container + "_" + chosen_project['name'],
                               self.application_description, self.application_type_batch,
                               self.user, self.execution_environment_name)

        mock_upload_application_to_pithos_task.delay.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               ApplicationViewSet.pithos_container + "_" + chosen_project['name'],
                               chosen_project['id'],
                               path.join(settings.TEMPORARY_FILE_STORAGE, self.application.name),
                               application_id, self.application.name, self.application_description)

    # Test for uploading an application when all the required information are provided
    # but there is already an application with the same name uploaded.
    def test_existent_name(self):
        # Create an application on the database.
        Application.objects.create(uuid=uuid.uuid4(), name="existing_application.jar",
                                   type=Application.BATCH)

        # file
        existing_application = SimpleUploadedFile("existing_application.jar", "Hello World")

        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'file': existing_application,
                                                   'type': self.application_type_batch,
                                                   'project_name': self.project_name,
                                                   'execution_environment_name': self.
                                                   execution_environment_name})

        # Assert the structure of the response.
        self._assert_bad_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomParseError.messages['filename_already_exists_error'])

    # Test for uploading an application when no description is provided.
    @mock.patch('backend.views.get_user_okeanos_projects')
    @mock.patch('backend.views.events.create_new_application')
    @mock.patch('backend.views.tasks.upload_application_to_pithos')
    def test_no_description(self, mock_upload_application_to_pithos_task,
                            mock_create_new_application_event, mock_get_user_okeanos_projects):
        # Configure return values for mocks.
        chosen_project = self.user_projects[0]
        mock_get_user_okeanos_projects.return_value = self.user_projects

        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'file': self.application,
                                                   'type': self.application_type_batch,
                                                   'project_name': self.project_name,
                                                   'execution_environment_name':
                                                       self.execution_environment_name})

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
            assert_called_with(application_id, self.application.name, chosen_project['id'],
                               ApplicationViewSet.pithos_container + "_" + chosen_project['name'],
                               "", self.application_type_batch, self.user,
                               self.execution_environment_name)

        mock_upload_application_to_pithos_task.delay.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               ApplicationViewSet.pithos_container + "_" + chosen_project['name'],
                               chosen_project['id'],
                               path.join(settings.TEMPORARY_FILE_STORAGE, self.application.name),
                               application_id, self.application.name, "")

    # Test for uploading an application when no execution environment name is provided.
    # Test for uploading an application when no description is provided.
    @mock.patch('backend.views.get_user_okeanos_projects')
    @mock.patch('backend.views.events.create_new_application')
    @mock.patch('backend.views.tasks.upload_application_to_pithos')
    def test_no_execution_environment_name(self, mock_upload_application_to_pithos_task,
                                           mock_create_new_application_event,
                                           mock_get_user_okeanos_projects):
        # Configure return values for mocks.
        chosen_project = self.user_projects[0]
        mock_get_user_okeanos_projects.return_value = self.user_projects

        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'file': self.application,
                                                   'type': self.application_type_batch,
                                                   'project_name': self.project_name,
                                                   'description': self.application_description})

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
            assert_called_with(application_id, self.application.name, chosen_project['id'],
                               ApplicationViewSet.pithos_container + "_" + chosen_project['name'],
                               self.application_description, self.application_type_batch,
                               self.user, "")

        mock_upload_application_to_pithos_task.delay.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               ApplicationViewSet.pithos_container + "_" + chosen_project['name'],
                               chosen_project['id'],
                               path.join(settings.TEMPORARY_FILE_STORAGE, self.application.name),
                               application_id, self.application.name, self.application_description)

    # Test for uploading an application when no file is provided.
    def test_no_file(self):

        # Make a request to upload an application.
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
    @mock.patch('backend.views.get_user_okeanos_projects')
    @mock.patch('backend.views.events.create_new_application')
    @mock.patch('backend.views.tasks.upload_application_to_pithos')
    def test_type_streaming(self, mock_upload_application_to_pithos_task,
                            mock_create_new_application_event, mock_get_user_okeanos_projects):
        # Configure return values for mocks.
        chosen_project = self.user_projects[0]
        mock_get_user_okeanos_projects.return_value = self.user_projects

        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'file': self.application,
                                                   'type': self.application_type_streaming,
                                                   'project_name': self.project_name,
                                                   'execution_environment_name': self.
                                                   execution_environment_name})

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
            assert_called_with(application_id, self.application.name, chosen_project['id'],
                               ApplicationViewSet.pithos_container + "_" + chosen_project['name'],
                               self.application_description, self.application_type_streaming,
                               self.user, self.execution_environment_name)

        mock_upload_application_to_pithos_task.delay.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               ApplicationViewSet.pithos_container + "_" + chosen_project['name'],
                               chosen_project['id'],
                               path.join(settings.TEMPORARY_FILE_STORAGE, self.application.name),
                               application_id, self.application.name, self.application_description)

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
    def test_no_project_name(self):
        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'file': self.application,
                                                   'type': self.application_type_batch,
                                                   'execution_environment_name': self.
                                                   execution_environment_name})

        # Assert the structure of the response.
        self._assert_bad_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomParseError.messages['no_project_error'])

    # Test for uploading an application when a wrong project is provided.
    @mock.patch('backend.views.get_user_okeanos_projects')
    def test_wrong_project_name(self, mock_get_user_okeanos_projects):
        # Configure return values for mocks.
        mock_get_user_okeanos_projects.return_value = self.user_projects

        # Make a request to upload an application.
        response = self.client.post("/api/apps/", {'description': self.application_description,
                                                   'file': self.application,
                                                   'type': self.application_type_batch,
                                                   'project_name': "a-wrong-project-name",
                                                   'execution_environment_name':
                                                   self.execution_environment_name})

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomCantDoError.messages['wrong_project_name'].
                         format(project_name="a-wrong-project-name"))

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
    """
    Contains tests for applications list API call.
    """

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
        # Make a request to list the existing applications.
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
            self.assertIn('type', application)
            self.assertIn('status', application)
            self.assertIn('deployed', application)

            self.assertIn('code', application['status'])
            self.assertIn('message', application['status'])
            self.assertIn('detail', application['status'])

    def _assert_success_request_response_content(self, response, offset=0):
        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['applications_list'])

        # Gather all the returned application names and assert the id of each application.
        returned_application_names = list()
        for application in response.data['data']:
            returned_application_names.append(application['name'])
            self.assertRegexpMatches(application['id'], r'^([^/.]+)$')

        # Gather all the expected application names.
        expected_application_names = list()
        for index in range(len(response.data['data'])):
            expected_application_names.append("application_{}.jar".format(index + offset))

        # Assert that every expected application name exists inside the returned application
        # names and that the sizes of these sets are equal.
        for expected_application_name in expected_application_names:
            self.assertIn(expected_application_name, returned_application_names)

        # Assert that the message, the code and the detail inside application status and the type
        # are correctly chosen.
        for application in response.data['data']:
            self.assertEqual(application['type'], Application.type_choices[
                int(Application.BATCH)][1])
            self.assertEqual(application['status']['message'],
                             Application.status_choices[int(application['status']['code'])][1])
            self.assertEqual(application['status']['detail'],
                             ResponseMessages.application_status_details[
                                 application['status']['message']])

        self.assertEqual(len(expected_application_names), len(returned_application_names))


class TestApplicationDetails(APITestCase):
    """
    Contains tests for application details API call.
    """

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
        self.assertIn('lambda_instances', response.data['data'][0])
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
        self.assertEqual(len(response.data['data'][0]['lambda_instances']), 0)

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


class TestApplicationDelete(APITestCase):
    """
    Contains tests for application delete API call.
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
        # Create a uuid.
        self.random_uuid = uuid.uuid4()

        # Save an application on the database with the specified uuid.
        self.app = Application.objects.create(uuid=self.random_uuid, name="application.jar",
                                              description="A description.", type=Application.BATCH)

        self.instance = LambdaInstance.objects.create(instance_info="{}", name="test_instance_name",
                                                      uuid=uuid.uuid4(), failure_message="",
                                                      status=0, started_batch=True,
                                                      started_streaming=False)

        self.conn = LambdaInstanceApplicationConnection.objects.create(
            lambda_instance=self.instance,
            application=self.app,
            started=False)

    # Test for deleting an application.
    @mock.patch('backend.views.tasks.delete_application_from_pithos')
    def test_application_delete(self, mock_delete_application_from_pithos_task):
        # Make a request to delete a specific application.
        response = self.client.delete("/api/apps/{random_uuid}/".
                                      format(random_uuid=self.random_uuid))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_delete'])

        # Assert that the proper tasks and views have been called.
        # Note that uuid is passed as a string and not as a UUID object. That is because,
        # Django url parser gives the provided on the url uuid as a string.
        mock_delete_application_from_pithos_task.delay.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               ApplicationViewSet.pithos_container, "application.jar",
                               "{random_uuid}".format(random_uuid=self.random_uuid))

    # Test for deleting an running application.
    @mock.patch('backend.views.tasks.delete_application_from_pithos')
    def test_running_application_delete(self, mock_delete_application_from_pithos_task):

        self.conn.started = True
        self.conn.save()

        # Make a request to delete a specific application.
        response = self.client.delete("/api/apps/{random_uuid}/".
                                      format(random_uuid=self.random_uuid))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)
        self.assertIn('status', response.data['errors'][0])
        self.assertIn('detail', response.data['errors'][0])

        # Assert the contents of the response
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         "Can't delete application application.jar while it is running. "
                         "Current lambda instances it is running are: test_instance_name")

    # Test for requesting to delete an application that doesn't exist.
    def test_non_existent_id(self):
        # Make a request to delete a specific application.
        response = self.client.delete("/api/apps/{random_uuid}/".format(random_uuid=uuid.uuid4()))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'], CustomNotFoundError.
                                                               messages['application_not_found'])


class TestApplicationDeploy(APITestCase):
    """
    Contains tests for application deploy API call.
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

        # Save an application and a lambda instance on the database.
        self.application_uuid = uuid.uuid4()
        self.lambda_instance_uuid = uuid.uuid4()

        Application.objects.create(uuid=self.application_uuid, name="application.jar",
                                   description="A description.", type=Application.BATCH)

        LambdaInstance.objects.create(uuid=self.lambda_instance_uuid, name="Lambda Instance 1",
                                      status=LambdaInstance.STARTED)

    # Test for deploying an application to a lambda instance.
    @mock.patch('backend.views.tasks.deploy_application')
    def test_application_deploy(self, mock_deploy_application_task):
        # Make a request to deploy a specific application.
        response = self.client.post("/api/apps/{application_uuid}/deploy/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_deploy'])

        # Assert that the proper tasks and views have been called.
        mock_deploy_application_task.delay.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               ApplicationViewSet.pithos_container,
                               "{lambda_instance_uuid}".format(
                                   lambda_instance_uuid=self.lambda_instance_uuid),
                               "{application_uuid}".format(application_uuid=self.application_uuid))

    # Test for request to deploy an application when lambda instance id is not provided.
    def test_no_lambda_instance_id(self):
        # Make a request to deploy a specific application without providing a lambda instance id.
        response = self.client.post("/api/apps/{application_uuid}/deploy/".
                                      format(application_uuid=self.application_uuid))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomParseError.messages['no_lambda_instance_id_error'])

    # Test for request to deploy an application when the specified lambda instance doesn't exist.
    def test_non_existent_lambda_instance(self):
        # Make a request to deploy a specific application.
        response = self.client.post("/api/apps/{application_uuid}/deploy/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": uuid.uuid4()})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['lambda_instance_not_found'])

    # Test for request to deploy an application when the specified application doesn't exist.
    def test_non_existent_application(self):
        # Make a request to deploy a specific application.
        response = self.client.post("/api/apps/{application_uuid}/deploy/".
                                      format(application_uuid=uuid.uuid4()),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['application_not_found'])

    # Test for request to deploy an application when the specified lambda instance status is not
    # STARTED.
    def test_lambda_instance_not_started(self):
        # Change the status of the lambda instance saved on the database.
        lambda_instance = LambdaInstance.objects.get(uuid=self.lambda_instance_uuid)

        lambda_instance_status = randint(1, len(LambdaInstance.status_choices) - 1)
        lambda_instance.status = "{lambda_instance_status}".\
            format(lambda_instance_status=lambda_instance_status)
        lambda_instance.save()

        # Make a request to deploy a specific application.
        response = self.client.post("/api/apps/{application_uuid}/deploy/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomCantDoError.messages['cant_do'].
                         format(action="deploy", object="an application",
                                status=LambdaInstance.status_choices[lambda_instance_status][1]))

    # Test for request to deploy an application on a lambda instance when it is already deployed.
    def test_already_deployed(self):
        # Create a connection between the lambda instance and the application on the database.
        lambda_instance = LambdaInstance.objects.get(uuid=self.lambda_instance_uuid)
        application = Application.objects.get(uuid=self.application_uuid)
        LambdaInstanceApplicationConnection.objects.create(lambda_instance=lambda_instance,
                                                           application=application)

        # Make a request to deploy a specific application.
        response = self.client.post("/api/apps/{application_uuid}/deploy/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomAlreadyDoneError.messages['application_already_deployed'])

    def _assert_error_response_structure(self, response):
        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)


class TestApplicationWithdraw(APITestCase):
    """
    Contains tests for application withdraw API call.
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

        # Save an application and a lambda instance on the database and create a connections
        # between them.
        self.application_uuid = uuid.uuid4()
        self.lambda_instance_uuid = uuid.uuid4()

        application = Application.objects.create(uuid=self.application_uuid,
                                                 name="application.jar",
                                                 description="A description.",
                                                 type=Application.BATCH)

        lambda_instance = LambdaInstance.objects.create(uuid=self.lambda_instance_uuid,
                                                        name="Lambda Instance 1",
                                                        status=LambdaInstance.STARTED)

        LambdaInstanceApplicationConnection.objects.create(application=application,
                                                           lambda_instance=lambda_instance)

    # Test for withdrawing an application from a specified lambda instance.
    @mock.patch('backend.views.tasks.withdraw_application')
    def test_application_withdraw(self, mock_withdraw_application_task):
        # Make a request to withdraw a specific application.
        response = self.client.post("/api/apps/{application_uuid}/withdraw/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_withdraw'])

        # Assert that the proper tasks and views have been called.
        mock_withdraw_application_task.delay.\
            assert_called_with("{lambda_instance_id}".
                               format(lambda_instance_id=self.lambda_instance_uuid),
                               "{application_id}".format(application_id=self.application_uuid))

    # Test for request to withdraw an application when lambda instance id is not provided.
    def test_no_lambda_instance_id(self):
        # Make a request to withdraw a specific application without providing a lambda instance id.
        response = self.client.post("/api/apps/{application_uuid}/withdraw/".
                                      format(application_uuid=self.application_uuid))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomParseError.messages['no_lambda_instance_id_error'])

    # Test for request to withdraw an application when the specified lambda instance doesn't exist.
    def test_non_existent_lambda_instance(self):
        # Make a request to withdraw a specific application.
        response = self.client.post("/api/apps/{application_uuid}/withdraw/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": uuid.uuid4()})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['lambda_instance_not_found'])

    # Test for request to withdraw an application when the specified application doesn't exist.
    def test_non_existent_application(self):
        # Make a request to withdraw a specific application.
        response = self.client.post("/api/apps/{application_uuid}/withdraw/".
                                      format(application_uuid=uuid.uuid4()),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['application_not_found'])

    # Test for request to withdraw an application when the specified lambda instance status is not
    # STARTED.
    def test_lambda_instance_not_started(self):
        # Change the status of the lambda instance saved on the database.
        lambda_instance = LambdaInstance.objects.get(uuid=self.lambda_instance_uuid)

        lambda_instance_status = randint(1, len(LambdaInstance.status_choices) - 1)
        lambda_instance.status = "{lambda_instance_status}".\
            format(lambda_instance_status=lambda_instance_status)
        lambda_instance.save()

        # Make a request to withdraw a specific application.
        response = self.client.post("/api/apps/{application_uuid}/withdraw/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomCantDoError.messages['cant_do'].
                         format(action="withdraw", object="an application",
                                status=LambdaInstance.status_choices[lambda_instance_status][1]))

    # Test for request to withdraw an application on a lambda instance when it is not deployed.
    def test_not_deployed(self):
        # Delete the connection between the lambda instance and the application.
        LambdaInstanceApplicationConnection.objects.all().delete()

        # Make a request to withdraw a specific application.
        response = self.client.post("/api/apps/{application_uuid}/withdraw/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomAlreadyDoneError.messages['application_not_deployed'])

    def _assert_error_response_structure(self, response):
        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)


class TestApplicationsListDeployed(APITestCase):
    """
    Contains tests for applications list deployed API call.
    """

    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    def setUp(self):
        # Create a user and force authenticate.
        self.user = User.objects.create(uuid=uuid.uuid4())
        self.client.force_authenticate(user=self.user)

        # Add a fake token to every request authentication header to be used by the API.
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN))

        # Save a lambda instance on the database and connect some applications on it.
        self.lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=self.lambda_instance_uuid,
                                                        name="Lambda Instance 1",
                                                        status=LambdaInstance.STARTED)

        self.number_of_applications = randint(0, 100)
        for i in range(self.number_of_applications):
            application = Application.objects.create(uuid=uuid.uuid4(),
                                                     name="application_{i}.jar".format(i=i),
                                                     type=Application.BATCH)
            LambdaInstanceApplicationConnection.objects.create(application=application,
                                                               lambda_instance=lambda_instance)

    # Test for listing deployed application on a specified lambda instance.
    def test_applications_list_deployed(self):
        # Make a request to list the deployed application on the specified lambda instance.
        response = self.client.get("/api/apps/{lambda_instance_id}/list-deployed/".
                                   format(lambda_instance_id=self.lambda_instance_uuid))

        # Assert the structure of the response.
        self._assert_success_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(len(response.data['data']), self.number_of_applications)

        self._assert_success_request_response_content(response)

    # Test for listing applications deployed on a lambda instance when there is no application
    # deployed.
    def test_applications_list_empty(self):
        # Delete all the connections between the lambda instance and the applications.
        LambdaInstanceApplicationConnection.objects.all().delete()

        # Make a request to list the deployed application on the specified lambda instance.
        response = self.client.get("/api/apps/{lambda_instance_id}/list-deployed/".
                                   format(lambda_instance_id=self.lambda_instance_uuid))

        # Assert the structure of the response.
        self._assert_success_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(len(response.data['data']), 0)

        self._assert_success_request_response_content(response)

    # Test for listing applications deployed on a lambda instance using pagination.
    def test_applications_list_pagination(self):
        # Make a request using both limit and offset parameters.
        limit = randint(0, 100)
        offset = randint(-100, 100)
        response = self.client.\
            get("/api/apps/{lambda_instance_id}/list-deployed/?limit={limit}&offset={offset}".
                format(lambda_instance_id=self.lambda_instance_uuid, limit=limit, offset=offset))

        # Assert the structure of the response.
        self._assert_success_request_response_structure(response)

        self.assertIn('pagination', response.data)

        # Assert the contents of the response.
        number_of_expected_applications = None
        if offset < 0:
            number_of_expected_applications = self.number_of_applications
        elif offset < self.number_of_applications:
            number_of_expected_applications = self.number_of_applications - offset
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
        response = self.client.\
            get("/api/apps/{lambda_instance_id}/list-deployed/?limit={limit}".
                format(lambda_instance_id=self.lambda_instance_uuid, limit=limit))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'], CustomParseError.
                                                               messages['limit_value_error'])

    # Test for listing applications deployed on a lambda instance when the lambda instance doesn't
    # exist.
    def test_non_existent_lambda_instance_id(self):
        # Make a request to list the applications deployed on a lambda instance.
        response = self.client.get("/api/apps/{random_uuid}/list-deployed/".
                                   format(random_uuid=uuid.uuid4()))

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
                         CustomNotFoundError.messages['lambda_instance_not_found'])

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

        # Gather all the returned application names and assert the id of each application.
        returned_application_names = list()
        for application in response.data['data']:
            returned_application_names.append(application['name'])
            self.assertRegexpMatches(application['id'], r'^([^/.]+)$')

        # Gather all the expected application names.
        expected_application_names = list()
        for index in range(len(response.data['data'])):
            expected_application_names.append("application_{}.jar".format(index + offset))

        # Assert that every expected application name exists inside the returned application
        # names and that the sizes of these sets are equal.
        for expected_application_name in expected_application_names:
            self.assertIn(expected_application_name, returned_application_names)

        self.assertEqual(len(expected_application_names), len(returned_application_names))


class TestApplicationStart(APITestCase):
    """
    Contains tests for application start API call.
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

        # Save an application and a lambda instance on the database and create a connections
        # between them.
        self.application_uuid = uuid.uuid4()
        self.lambda_instance_uuid = uuid.uuid4()

        self.application = Application.objects.create(uuid=self.application_uuid,
                                                      name="application.jar",
                                                      description="A description.",
                                                      type=Application.BATCH,
                                                      execution_environment_name="Stream")

        self.lambda_instance = LambdaInstance.objects.create(uuid=self.lambda_instance_uuid,
                                                             name="Lambda Instance 1",
                                                             status=LambdaInstance.STARTED)

        self.connection = LambdaInstanceApplicationConnection.objects.\
            create(application=self.application, lambda_instance=self.lambda_instance)

    # Test for starting an application on a specified lambda instance that it is already deployed.
    @mock.patch('backend.views.tasks.start_stop_application')
    def test_application_start_batch(self, mock_start_stop_application_task):
        # Make a request to start the application.
        response = self.client.post("/api/apps/{application_uuid}/start/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_start'])

        # Assert that the proper tasks and views have been called.
        mock_start_stop_application_task.delay.\
            assert_called_with(lambda_instance_uuid=self.lambda_instance_uuid,
                               app_uuid="{application_id}".
                               format(application_id=self.application_uuid),
                               app_action="start", app_type="batch",
                               jar_filename="application.jar",
                               execution_environment_name="Stream")

    # Test for starting an application on a specified lambda instance that it is already deployed.
    @mock.patch('backend.views.tasks.start_stop_application')
    def test_application_start_streaming(self, mock_start_stop_application_task):
        # Change the type of the application from batch to streaming.
        self.application.type = Application.STREAMING
        self.application.save()

        # Make a request to start the application.
        response = self.client.post("/api/apps/{application_uuid}/start/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_start'])

        # Assert that the proper tasks and views have been called.
        mock_start_stop_application_task.delay.\
            assert_called_with(lambda_instance_uuid=self.lambda_instance_uuid,
                               app_uuid="{application_id}".
                               format(application_id=self.application_uuid),
                               app_action="start", app_type="streaming",
                               jar_filename="application.jar",
                               execution_environment_name="Stream")

    # Test for request to start an application when the lambda instance id is not provided.
    def test_no_lambda_instance_id(self):
        # Make a request to start the application without providing a lambda instance id.
        response = self.client.post("/api/apps/{application_uuid}/start/".
                                      format(application_uuid=self.application_uuid))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomParseError.messages['no_lambda_instance_id_error'])

    # Test for request to start an application when the lambda instance doesn't exist.
    def test_non_existent_lambda_instance(self):
        # Make a request to start the application with a random lambda instance id.
        response = self.client.post("/api/apps/{application_uuid}/start/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": uuid.uuid4()})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['lambda_instance_not_found'])

    # Test for request to start an application when the application doesn't exist.
    def test_non_existent_application(self):
        # Make a request to start an application with a random id.
        response = self.client.post("/api/apps/{application_uuid}/start/".
                                      format(application_uuid=uuid.uuid4()),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['application_not_found'])

    # Test for request to start an application when the lambda instance is not started.
    def test_lambda_instance_not_started(self):
        # Change the status of the lambda instance saved on the database.
        lambda_instance = LambdaInstance.objects.get(uuid=self.lambda_instance_uuid)

        lambda_instance_status = randint(1, len(LambdaInstance.status_choices) - 1)
        lambda_instance.status = "{lambda_instance_status}".\
            format(lambda_instance_status=lambda_instance_status)
        lambda_instance.save()

        # Make a request to start the application.
        response = self.client.post("/api/apps/{application_uuid}/start/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomCantDoError.messages['cant_do'].
                         format(action="start/stop", object="an application",
                                status=LambdaInstance.status_choices[lambda_instance_status][1]))

    # Test for request to start an application when the corresponding slot has already been taken.
    def test_already_started_batch(self):
        # Create a new application that will already be started.
        application_2 = Application.objects.create(uuid=uuid.uuid4(),
                                                   name="application_2.jar",
                                                   description="A second description.",
                                                   type=Application.BATCH)

        LambdaInstanceApplicationConnection.objects.create(application=application_2,
                                                           lambda_instance=self.lambda_instance,
                                                           started=True)

        self.lambda_instance.started_batch = True
        self.lambda_instance.save()

        # Make a request to start the application.
        response = self.client.post("/api/apps/{application_uuid}/start/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'], CustomAlreadyDoneError.
                         messages['job_already_started'].format(type="batch"))

    # Test for request to start an application when the corresponding slot has already been taken.
    def test_already_started_streaming(self):
        # Change the type of the application to streaming.
        self.application.type = Application.STREAMING
        self.application.save()

        # Create a new application that will already be started.
        application_2 = Application.objects.create(uuid=uuid.uuid4(),
                                                   name="application_2.jar",
                                                   description="A second description.",
                                                   type=Application.STREAMING)

        LambdaInstanceApplicationConnection.objects.create(application=application_2,
                                                           lambda_instance=self.lambda_instance,
                                                           started=True)

        self.lambda_instance.started_streaming = True
        self.lambda_instance.save()

        # Make a request to start the application.
        response = self.client.post("/api/apps/{application_uuid}/start/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'], CustomAlreadyDoneError.
                         messages['job_already_started'].format(type="streaming"))

    # Test for request to start an application when it is already started.
    def test_already_started(self):
        # Make the application already started.
        self.connection.started = True
        self.connection.save()

        # Make a request to start the application.
        response = self.client.post("/api/apps/{application_uuid}/start/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'], CustomAlreadyDoneError.
                         messages['application_already_started'])

    # Test for request to start an application when it is not already deployed.
    def test_not_deployed(self):
        # Delete the connection between the application and the lambda instance.
        self.connection.delete()

        # Make a request to start the application.
        response = self.client.post("/api/apps/{application_uuid}/start/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'], CustomNotFoundError.
                         messages['application_not_deployed_on_instance'])

    def _assert_error_response_structure(self, response):
        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)


class TestApplicationStop(APITestCase):
    """
    Contains tests for application stop API call.
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

        # Save an application and a lambda instance on the database and create a connections
        # between them.
        self.application_uuid = uuid.uuid4()
        self.lambda_instance_uuid = uuid.uuid4()

        self.application = Application.objects.create(uuid=self.application_uuid,
                                                      name="application.jar",
                                                      description="A description.",
                                                      type=Application.BATCH,
                                                      execution_environment_name="Stream")

        self.lambda_instance = LambdaInstance.objects.create(uuid=self.lambda_instance_uuid,
                                                             name="Lambda Instance 1",
                                                             status=LambdaInstance.STARTED,
                                                             started_batch=True,
                                                             started_streaming=True)

        self.connection = LambdaInstanceApplicationConnection.objects.\
            create(application=self.application, lambda_instance=self.lambda_instance,
                   started=True)

    # Test for stopping an application on a specified lambda instance that it is already started.
    @mock.patch('backend.views.tasks.start_stop_application')
    def test_application_stop_batch(self, mock_start_stop_application_task):
        # Make a request to stop the application.
        response = self.client.post("/api/apps/{application_uuid}/stop/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_stop'])

        # Assert that the proper tasks and views have been called.
        mock_start_stop_application_task.delay.\
            assert_called_with(lambda_instance_uuid=self.lambda_instance_uuid,
                               app_uuid="{application_id}".
                               format(application_id=self.application_uuid),
                               app_action="stop", app_type="batch",
                               execution_environment_name="Stream")

    # Test for stopping an application on a specified lambda instance that it is already started.
    @mock.patch('backend.views.tasks.start_stop_application')
    def test_application_stop_streaming(self, mock_start_stop_application_task):
        # Change the type of the application from batch to streaming.
        self.application.type = Application.STREAMING
        self.application.save()

        # Make a request to stop the application.
        response = self.client.post("/api/apps/{application_uuid}/stop/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['application_stop'])

        # Assert that the proper tasks and views have been called.
        mock_start_stop_application_task.delay.\
            assert_called_with(lambda_instance_uuid=self.lambda_instance_uuid,
                               app_uuid="{application_id}".
                               format(application_id=self.application_uuid),
                               app_action="stop", app_type="streaming",
                               execution_environment_name="Stream")

    # Test for request to stop an application when the lambda instance id is not provided.
    def test_no_lambda_instance_id(self):
        # Make a request to stop the application without providing a lambda instance id.
        response = self.client.post("/api/apps/{application_uuid}/stop/".
                                      format(application_uuid=self.application_uuid))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomParseError.messages['no_lambda_instance_id_error'])

    # Test for request to stop an application when the lambda instance doesn't exist.
    def test_non_existent_lambda_instance(self):
        # Make a request to stop the application with a random lambda instance id.
        response = self.client.post("/api/apps/{application_uuid}/stop/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": uuid.uuid4()})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['lambda_instance_not_found'])

    # Test for request to stop an application when the application doesn't exist.
    def test_non_existent_application(self):
        # Make a request to stop an application with a random id.
        response = self.client.post("/api/apps/{application_uuid}/stop/".
                                      format(application_uuid=uuid.uuid4()),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['application_not_found'])

    # Test for request to stop an application when the lambda instance is not started.
    def test_lambda_instance_not_started(self):
        # Change the status of the lambda instance saved on the database.
        lambda_instance = LambdaInstance.objects.get(uuid=self.lambda_instance_uuid)

        lambda_instance_status = randint(1, len(LambdaInstance.status_choices) - 1)
        lambda_instance.status = "{lambda_instance_status}".\
            format(lambda_instance_status=lambda_instance_status)
        lambda_instance.save()

        # Make a request to stop the application.
        response = self.client.post("/api/apps/{application_uuid}/stop/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomCantDoError.messages['cant_do'].
                         format(action="start/stop", object="an application",
                                status=LambdaInstance.status_choices[lambda_instance_status][1]))

    # Test for request to stop an application when it is already stopped.
    def test_already_stopped(self):
        # Make the application already stopped.
        self.connection.started = False
        self.connection.save()

        self.lambda_instance.started_batch = False
        self.lambda_instance.started_streaming = False

        # Make a request to stop the application.
        response = self.client.post("/api/apps/{application_uuid}/stop/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'], CustomAlreadyDoneError.
                         messages['application_already_stopped'])

    # Test for request to stop an application when it is not already deployed.
    def test_not_deployed(self):
        # Delete the connection between the application and the lambda instance.
        self.connection.delete()

        # Make a request to stop the application.
        response = self.client.post("/api/apps/{application_uuid}/stop/".
                                      format(application_uuid=self.application_uuid),
                                    {"lambda_instance_id": self.lambda_instance_uuid})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert the structure of the response.
        self._assert_error_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['errors'][0]['detail'], CustomNotFoundError.
                         messages['application_not_deployed_on_instance'])

    def _assert_error_response_structure(self, response):
        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)


class TestApplicationsCount(APITestCase):
    """
    Contains tests for Applications count API call.
    """

    def setUp(self):
        # Create a user and force authenticate.
        self.user = User.objects.create(uuid=uuid.uuid4())
        self.client.force_authenticate(user=self.user)

        # Save some applications on the database.
        self.number_of_applications = randint(0, 100)
        for i in range(self.number_of_applications):
            Application.objects.create(uuid=uuid.uuid4(), type=Application.BATCH,
                                       name="application_{}.jar".format(i))

    # Test for getting the count of the applications.
    def test_applications_count(self):
        # Make a request to get the count of the applications.
        response = self.client.get("/api/apps/count/")

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the structure of the response.
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response.
        self.assertEqual(len(response.data['data']), 1)

        for item in response.data['data']:
            self.assertIn('count', item)

        self.assertEqual(response.data['data'][0]['count'], self.number_of_applications)
