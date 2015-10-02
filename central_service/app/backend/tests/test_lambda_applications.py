from mock import patch
from backend.models import User, Token, LambdaApplication
from backend.response_messages import ResponseMessages
from backend.exceptions import CustomAlreadyDoneError, CustomNotFoundError, CustomParseError
from rest_framework.test import APITestCase
from rest_framework import status as rest_status
import copy
import uuid
from random import randint
from math import ceil


class TestLambdaApplications(APITestCase):
    """
    Test case for the Lambda Applications calls of the central ~okeanos
    LoD Service.
    """

    AUTHENTICATION_TOKEN = "some_token"

    def setUp(self):
        self.authenticated_user = User.objects.create(uuid=uuid.uuid4())

        self.client.force_authenticate(user=self.authenticated_user)

        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN))

        self.create_request_data = {
            'uuid': '24b8a635-8d71-4016-b8f5-c4a14348ed1f',
            'name': 'test_lambda_application',
            'description': 'test_content',
            'status': '0',
            'failure_message': 'OK',
        }

    # ----- CREATE Tests -----
    @patch('backend.views.events.createLambdaApplication.delay')
    def test_create_non_existent_application(self, mock_create_task):
        """
        Tests API for creation of non-existent application in the database with the same
        uuid.
        :param mock_create_task: Mock object for the celery creation task.
        """

        response = self.client.post("/api/lambda_applications/", self.create_request_data,
                                    format='json')

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_202_ACCEPTED)
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)
        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])
        self.assertIn('id', response.data['data'])

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_202_ACCEPTED, response.data['status']['code'])
        self.assertEqual(ResponseMessages.short_descriptions['lambda_applications_create'],
                         response.data['status']['short_description'])
        self.assertEqual(self.create_request_data['uuid'], response.data['data']['id'])

        self.assertTrue(mock_create_task.called)

    @patch('backend.views.events.createLambdaApplication.delay')
    def test_create_existent_application(self, mock_create_task):
        """
        Tests API for creation of already existent application with the same UUID.
        :param mock_create_task: Mock object for the celery creation task.
        """

        current_user = User.objects.get(uuid=self.authenticated_user.uuid)

        patched_req_data = copy.deepcopy(self.create_request_data)
        patched_req_data['owner'] = current_user
        LambdaApplication.objects.create(**patched_req_data)

        response = self.client.post("/api/lambda_applications/", self.create_request_data,
                                    format='json')

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_409_CONFLICT)
        self.assertIn('errors', response.data)
        for err in response.data['errors']:
            self.assertIn('status', err)
            self.assertIn('detail', err)

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_409_CONFLICT, response.data['errors'][0]['status'])
        self.assertEqual(CustomAlreadyDoneError.messages['lambda_application_already_exists'],
                         response.data['errors'][0]['detail'])

        self.assertFalse(mock_create_task.called)

    # ----- Destroy Tests -----
    @patch('backend.views.events.deleteLambdaApplication.delay')
    def test_destroy_existent_application(self, mock_delete_task):
        """
        Tests API for deletion of already existent application with the specified
        UUID in the db.
        :param mock_delete_task: Mock object for the celery deletion task.
        """

        current_user = User.objects.get(uuid=self.authenticated_user.uuid)

        patched_req_data = copy.deepcopy(self.create_request_data)
        patched_req_data['owner'] = current_user
        LambdaApplication.objects.create(**patched_req_data)

        response = self.client.delete(
            "/api/lambda_applications/{id}/".format(id=self.create_request_data['uuid']),
            format='json'
        )

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_202_ACCEPTED)
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)
        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])
        self.assertIn('id', response.data['data'])

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_202_ACCEPTED, response.data['status']['code'])
        self.assertEqual(ResponseMessages.short_descriptions['lambda_applications_delete'],
                         response.data['status']['short_description'])
        self.assertEqual(self.create_request_data['uuid'], response.data['data']['id'])

        self.assertTrue(mock_delete_task.called)

    @patch('backend.views.events.deleteLambdaApplication.delay')
    def test_destroy_non_existent_application(self, mock_delete_task):
        """
        Tests API for deletion of non-existent application with the specified
        UUID in the db.
        :param mock_delete_task: Mock object for the celery deletion task.
        """

        response = self.client.delete(
            "/api/lambda_applications/{id}/".format(id=self.create_request_data['uuid']),
            format='json'
        )

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_404_NOT_FOUND)
        self.assertIn('errors', response.data)
        for err in response.data['errors']:
            self.assertIn('status', err)
            self.assertIn('detail', err)

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_404_NOT_FOUND, response.data['errors'][0]['status'])
        self.assertEqual(CustomNotFoundError.messages['application_not_found'],
                         response.data['errors'][0]['detail'])

        self.assertFalse(mock_delete_task.called)

    @patch('backend.views.events.deleteLambdaApplication.delay')
    def test_destroy_another_users_application(self, mock_delete_task):
        """
        Tests API for deletion of an application belonging to another user.
        :param mock_delete_task: Mock object for the celery deletion task.
        """
        other_uuid = uuid.uuid4()
        while(self.create_request_data['uuid'] == other_uuid):
            other_uuid = uuid.uuid4()

        patched_req_data = copy.deepcopy(self.create_request_data)
        patched_req_data['owner'] = User.objects.create(uuid=other_uuid)
        LambdaApplication.objects.create(**patched_req_data)

        response = self.client.delete(
            "/api/lambda_applications/{id}/".format(id=self.create_request_data['uuid']),
            format='json'
        )

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_404_NOT_FOUND)
        self.assertIn('errors', response.data)
        for err in response.data['errors']:
            self.assertIn('status', err)
            self.assertIn('detail', err)

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_404_NOT_FOUND, response.data['errors'][0]['status'])
        self.assertEqual(CustomNotFoundError.messages['application_not_found'],
                         response.data['errors'][0]['detail'])

        self.assertFalse(mock_delete_task.called)

    # ----- Update Tests -----
    @patch('backend.events.updateLambdaApplicationStatus.delay')
    def test_update_status_of_existent_application(self, mock_update_task):
        """
        Tests API for status update of an existent application in the database.
        :param mock_update_task: Mock object for the celery update task.
        """
        current_user = User.objects.get(uuid=self.authenticated_user.uuid)

        patched_req_data = copy.deepcopy(self.create_request_data)
        patched_req_data['owner'] = current_user
        LambdaApplication.objects.create(**patched_req_data)

        update_args = {
            'status': '21',
            'failure_message': 'Flink failed.',
        }

        response = self.client.post(
            "/api/lambda_applications/{id}/status/".format(id=self.create_request_data['uuid']),
            update_args,
            format='json'
        )

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_202_ACCEPTED)
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)
        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])
        self.assertIn('id', response.data['data'])

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_202_ACCEPTED, response.data['status']['code'])
        self.assertEqual(ResponseMessages.short_descriptions['lambda_applications_update'],
                         response.data['status']['short_description'])
        self.assertEqual(self.create_request_data['uuid'], response.data['data']['id'])

        self.assertTrue(mock_update_task.called)


    @patch('backend.events.updateLambdaApplicationStatus.delay')
    def test_update_status_of_non_existent_application(self, mock_update_task):
        """
        Tests API for status update of a non-existent application with the specified
        if in the database.
        :param mock_update_task: Mock object for the celery update task.
        """

        update_args = {
            'status': '21',
            'failure_message': 'Flink failed.',
        }

        response = self.client.post(
            "/api/lambda_applications/{id}/status/".format(id=self.create_request_data['uuid']),
            update_args,
            format='json'
        )

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_404_NOT_FOUND)
        self.assertIn('errors', response.data)
        for err in response.data['errors']:
            self.assertIn('status', err)
            self.assertIn('detail', err)

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_404_NOT_FOUND, response.data['errors'][0]['status'])
        self.assertEqual(CustomNotFoundError.messages['application_not_found'],
                         response.data['errors'][0]['detail'])

        self.assertFalse(mock_update_task.called)

    @patch('backend.events.updateLambdaApplicationStatus.delay')
    def test_update_another_users_application(self, mock_update_task):
        """
        Tests API for status update of an application belonging to another user.
        :param mock_update_task: Mock object for the celery update task.
        """

        other_uuid = uuid.uuid4()
        while(self.create_request_data['uuid'] == other_uuid):
            other_uuid = uuid.uuid4()

        patched_req_data = copy.deepcopy(self.create_request_data)
        patched_req_data['owner'] = User.objects.create(uuid=other_uuid)
        LambdaApplication.objects.create(**patched_req_data)

        update_args = {
            'status': '21',
            'failure_message': 'Flink failed.',
        }
        response = self.client.post(
            "/api/lambda_applications/{id}/status/".format(id=self.create_request_data['uuid']),
            update_args,
            format='json'
        )

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_404_NOT_FOUND)
        self.assertIn('errors', response.data)
        for err in response.data['errors']:
            self.assertIn('status', err)
            self.assertIn('detail', err)

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_404_NOT_FOUND, response.data['errors'][0]['status'])
        self.assertEqual(CustomNotFoundError.messages['application_not_found'],
                         response.data['errors'][0]['detail'])

        self.assertFalse(mock_update_task.called)

    @patch('backend.events.updateLambdaApplicationStatus.delay')
    def test_update_with_same_status(self, mock_update_task):
        """
        Tests API for status update of an application which already has the status
        to be changed to.
        :param mock_update_task: Mock object for the celery update task.
        """
        current_user = User.objects.get(uuid=self.authenticated_user.uuid)

        patched_req_data = copy.deepcopy(self.create_request_data)
        patched_req_data['owner'] = current_user
        LambdaApplication.objects.create(**patched_req_data)

        update_args = {
            'status': self.create_request_data['status'],
            'failure_message': self.create_request_data['failure_message'],
        }

        response = self.client.post(
            "/api/lambda_applications/{id}/status/".format(id=self.create_request_data['uuid']),
            update_args,
            format='json'
        )

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_409_CONFLICT)
        self.assertIn('errors', response.data)
        for err in response.data['errors']:
            self.assertIn('status', err)
            self.assertIn('detail', err)

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_409_CONFLICT, response.data['errors'][0]['status'])
        self.assertEqual(
            CustomAlreadyDoneError.messages['lambda_application_already'].format(
                state=self.create_request_data['status']
            ),
            response.data['errors'][0]['detail']
        )

        self.assertFalse(mock_update_task.called)

    # ----- List Tests -----
    def populate_database(self, user_count_range=(1,9), applications_count_range=(11,100),
                          authenticated_user_inclusion=True):
        """
        Creates dummy user and lambda applications data in the database for testing.
        :param user_count_range: Range for random number of users to be created.
        :param applications_count_range: Range for random number of applications to be created.
        :param authenticated_user_inclusion: Equip the authenticated user with lambda applications
        or not.
        """

        current_user = User.objects.get(uuid=self.authenticated_user.uuid)
        # create a number of users
        self.user_count = randint(*user_count_range)
        created_users = [current_user,] if authenticated_user_inclusion else []
        for i in range(self.user_count):
            uuid_to_use = uuid.uuid4()
            while uuid_to_use == self.authenticated_user.uuid:
                uuid_to_use = uuid.uuid4()
            created_users.append(User.objects.create(uuid=uuid.uuid4()))

        # crate a number of applications
        self.applications_count = randint(*applications_count_range)
        created_applications = []
        for i in range(self.applications_count):
            LambdaApplication.objects.create(uuid=uuid.uuid4(), description="inst_info",
                                          owner=created_users[i%(self.user_count)],
                                          status=0)

    def test_list_users_applications_non_empty(self):
        """
        Tests API for applications list when the authenticated user owns some.
        """

        self.populate_database()

        response = self.client.get("/api/lambda_applications/", format='json')

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)
        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])
        for record in response.data['data']:
            self.assertIn('uuid', record)
            self.assertIn('name', record)
            self.assertIn('description', record)
            self.assertIn('status', record)
            self.assertIn('failure_message', record)

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_200_OK, response.data['status']['code'])
        self.assertEqual(ResponseMessages.short_descriptions['lambda_applications_list'],
                         response.data['status']['short_description'])
        number_of_lambda_applications = int(ceil(float(self.applications_count)/self.user_count))
        self.assertEqual(number_of_lambda_applications,
                         len(response.data['data']))


    def test_list_users_applications_empty(self):
        """
        Tests API for applications list when the authenticated user owns none.
        """
        self.populate_database(authenticated_user_inclusion=False)

        response = self.client.get("/api/lambda_applications/", format='json')

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)
        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])
        for record in response.data['data']:
            self.assertIn('uuid', record)
            self.assertIn('name', record)
            self.assertIn('description', record)
            self.assertIn('status', record)
            self.assertIn('failure_message', record)

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_200_OK, response.data['status']['code'])
        self.assertEqual(ResponseMessages.short_descriptions['lambda_applications_list'],
                         response.data['status']['short_description'])

        self.assertFalse(response.data['data'])


    def test_list_users_applications_paginated(self):
        """
        Tests APi for paginated list of lambda applications owned by the authenticated
        user.
        """

        self.populate_database()
        # Make a request using both limit and offset parameters.
        limit = randint(0, 100)
        offset = randint(-100, 100)

        response = self.client.get("/api/lambda_applications/"
                                   "?limit={limit}&offset={offset}".format(limit=limit,
                                   offset=offset), format='json')

        number_of_lambda_applications = int(ceil(float(self.applications_count)/self.user_count))

        self.assertIn('pagination', response.data)

        # Assert the contents of the response.
        number_of_expected_lambda_applications = None
        if offset < 0:
            number_of_expected_lambda_applications = number_of_lambda_applications
        elif offset < number_of_lambda_applications:
            number_of_expected_lambda_applications = number_of_lambda_applications - offset
        else:
            number_of_expected_lambda_applications = 0

        if number_of_expected_lambda_applications >= limit:
            self.assertEqual(len(response.data['data']), limit)
        else:
            self.assertEqual(len(response.data['data']), number_of_expected_lambda_applications)


        self.assertEqual(rest_status.HTTP_200_OK, response.data['status']['code'])
        self.assertEqual(ResponseMessages.short_descriptions['lambda_applications_list'],
                     response.data['status']['short_description'])


    def test_negative_pagination(self):
        """
        Tests APi for paginated list of lambda applications owned by the authenticated
        user when the API user passes negative pagination params.
        """

        # Make a request to list the lambda applications.
        limit = randint(-100, -1)
        response = self.client.get("/api/lambda_applications/?limit={limit}".format(limit=limit))

        # Assert the response code.
        self.assertEqual(response.status_code, rest_status.HTTP_400_BAD_REQUEST)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response
        self.assertEqual(response.data['errors'][0]['status'], rest_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'], CustomParseError.
                                                               messages['limit_value_error'])

    # ----- Count Tests -----
    def test_count(self):
        """
        Tests API for count of active lambda applications.
        """

        self.populate_database()

        response = self.client.get("/api/lambda_applications/count", format='json')

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)
        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])
        self.assertIn('count', response.data['data'])

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_200_OK, response.data['status']['code'])
        self.assertEqual(ResponseMessages.short_descriptions['lambda_applications_count'],
                         response.data['status']['short_description'])

        number_of_lambda_applications = \
            LambdaApplication.objects.filter(status="0").count()

        self.assertEqual(str(number_of_lambda_applications), response.data['data']['count'])

    def test_count_zero(self):
        """
        Tests API for count of active lambda applications when the user owns none.
        """

        self.populate_database(authenticated_user_inclusion=False)

        response = self.client.get("/api/lambda_applications/count", format='json')

        # Structure of the response assertions
        self.assertEqual(response.status_code, rest_status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)
        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])
        self.assertIn('count', response.data['data'])

        # Content of the response assertions
        self.assertEqual(rest_status.HTTP_200_OK, response.data['status']['code'])
        self.assertEqual(ResponseMessages.short_descriptions['lambda_applications_count'],
                         response.data['status']['short_description'])

        number_of_lambda_applications = \
            LambdaApplication.objects.filter(status="0").count()

        self.assertEqual(str(number_of_lambda_applications), response.data['data']['count'])