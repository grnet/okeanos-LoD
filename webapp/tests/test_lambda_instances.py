import uuid
import mock
import json

from random import randint

from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import User, LambdaInstance
from backend.response_messages import ResponseMessages
from backend.exceptions import CustomParseError


class TestLambdaInstanceCreate(APITestCase):
    """
    Contains tests for lambda instance create API call.
    """

    class CeleryTaskResponse:
        """
        Class that emulates the response given by a Celery task when its .delay method is called.
        """

        def __init__(self, id=None):
            self.id = id

    # Define ~okeanos authentication url.
    AUTHENTICATION_URL = "https://accounts.okeanos.grnet.gr/identity/v2.0"
    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    # A request to create a lambda instance should include the following parameters:
    lambda_information = {'project_name': "lambda.grnet.gr",
                          'instance_name': "My Lambda Instance",
                          'network_request': 1,
                          'master_name': "lambda-master",
                          'vcpus_master': 4,
                          'vcpus_slave': 4,
                          'ram_master': 4096,
                          'ram_slave': 4096,
                          'disk_master': 20,
                          'disk_slave': 20,
                          'slaves': 2,
                          'ip_allocation': "master",
                          'public_key_name': ["key-1", "key-2"]}

    # Gather required fields.
    required_keys = ['project_name',
                     'instance_name',
                     'master_name',
                     'vcpus_master',
                     'vcpus_slave',
                     'ram_master',
                     'ram_slave',
                     'disk_master',
                     'disk_slave',
                     'slaves']

    # Gather fields that should take values from a specified list.
    restricted_keys = ['vcpus_master',
                       'vcpus_slave',
                       'ram_master',
                       'ram_slave',
                       'disk_master',
                       'disk_slave',
                       'ip_allocation']

    def setUp(self):
        # Create a user and force authenticate.
        self.user = User.objects.create(uuid=uuid.uuid4())
        self.client.force_authenticate(user=self.user)

        # Add a fake token to every request authentication header to be used by the API and
        # a application/json as the content type.
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN),
                                HTTP_CONTENT_TYPE='application/json')

    # Test for creating a lambda instance.
    @mock.patch('backend.views.tasks.create_lambda_instance.delay',
                return_value=CeleryTaskResponse(uuid.uuid4()))
    def test_lambda_instance_create(self, mock_create_lambda_instance_task):

        # Make a request to create a lambda instance.
        response = self.client.post("/api/lambda-instance/", self.lambda_information, format='json')

        # Assert the status code of the response.
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

        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['lambda_instance_create'])

        self.assertIsInstance(response.data['data'][0]['id'], uuid.UUID)

        self.assertRegexpMatches(response.data['data'][0]['links']['self'],
                                 r'^http://testserver/api/lambda-instances/([^/.]+)$')

        # Assert that the proper tasks and views have been called.
        # Note: Can't user assert_called_with because the object provided to the mocked object is
        # created inside the view and cannot be reproduced here to be given as argument in
        # assert_called_with. That is why we test if the mocked object was called and if the data
        # of its first argument are equal to the data we provided.
        self.assertTrue(mock_create_lambda_instance_task.called)
        self.assertEqual(mock_create_lambda_instance_task.call_args[0][0].data,
                         json.loads(json.dumps(self.lambda_information)))

    # Test for request to create a lambda instance without providing each one of the mandatory
    # information.
    def test_field_not_provided(self):

        # Iterate over the required keys removing one each time and making a request to create
        # a lambda instance with the missing key.
        for required_key in self.required_keys:
            # Make a copy of the full lambda information.
            lambda_information = self.lambda_information.copy()

            # Remove the current required key from the copied lambda information.
            del lambda_information[required_key]

            # Make a request to create a lambda instance.
            response = self.client.post("/api/lambda-instance/", lambda_information, format='json')

            # Assert the status code of the response.
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            # Assert the structure of the response.
            self.assertIn('errors', response.data)

            self.assertEqual(len(response.data['errors']), 1)

            for error in response.data['errors']:
                self.assertIn('status', error)
                self.assertIn('detail', error)

                self.assertEqual(len(error['detail']), 1)

            # Assert the contents of the response.
            self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['errors'][0]['detail'][0],
                             "{field}: This field is required.".format(field=required_key))

    # Test for request to create a lambda instance without providing any information.
    def test_no_field_provided(self):
        # Make a request to create a lambda instance.
        response = self.client.post("/api/lambda-instance/", {}, format='json')

        # Assert the status code of the response.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), len(self.required_keys))

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

            self.assertEqual(len(error['detail']), 1)

        # Assert the contents of the response.
        # Gather all the error messages in a list.
        error_messages = list()
        for error in response.data['errors']:
            self.assertEqual(error['status'], status.HTTP_400_BAD_REQUEST)
            error_messages.append(error['detail'][0])

        for required_key in self.required_keys:
            self.assertIn("{field}: This field is required.".format(field=required_key),
                          error_messages)

    # Test for request to create a lambda instance when wrong values are provided.
    def test_wrong_values(self):
        # Make a request to create a lambda instance.
        response = self.client.post("/api/lambda-instance/",
                                    {'project_name': "lambda.grnet.gr",
                                     'instance_name': "My Lambda Instance",
                                     'network_request': 1,
                                     'master_name': "lambda-master",
                                     'vcpus_master': 5,
                                     'vcpus_slave': 1,
                                     'ram_master': 4097,
                                     'ram_slave': 1000000,
                                     'disk_master': 21,
                                     'disk_slave': 33,
                                     'slaves': 2,
                                     'ip_allocation': "Hello World",
                                     'public_key_name': ["key-1", "key-2"]},
                                    format='json')

        # Assert the status code of the response.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), len(self.restricted_keys))

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

            self.assertEqual(len(error['detail']), 1)

        # Assert the contents of the response.
        # Gather all the error messages in a list.
        error_messages = list()
        for error in response.data['errors']:
            self.assertEqual(error['status'], status.HTTP_400_BAD_REQUEST)
            error_messages.append(error['detail'][0])

        self.assertIn("vcpus_master: Wrong Number of master vcpus, available choices [2, 4, 8].",
                      error_messages)
        self.assertIn("vcpus_slave: Wrong Number of slave vcpus, available choices [2, 4, 8].",
                      error_messages)
        self.assertIn("disk_master: Wrong Size of master disk, available choices "
                      "[5, 10, 20, 40, 60, 80, 100].", error_messages)
        self.assertIn("disk_slave: Wrong Size of slave disk, available choices "
                      "[5, 10, 20, 40, 60, 80, 100].", error_messages)
        self.assertIn("ram_master: Wrong Amount of master ram, available choices "
                      "[512, 1024, 2048, 4096, 6144, 8192].", error_messages)
        self.assertIn("ram_slave: Wrong Amount of slave ram, available choices "
                      "[512, 1024, 2048, 4096, 6144, 8192].", error_messages)
        self.assertIn("ip_allocation: Wrong choice for ip_allocation, available choices "
                      "['all', 'none', 'master'].", error_messages)


class TestLambdaInstancesList(APITestCase):
    """
    Contains tests for lambda instances list API call.
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

    # Test for listing lambda instances.
    def test_lambda_instances_list(self):
        # Create some lambda instances on the database.
        number_of_lambda_instances = randint(0, 100)
        for i in range(number_of_lambda_instances):
            LambdaInstance.objects.create(uuid=uuid.uuid4(),
                                          name="lambda_instance_{i}".format(i=i))

        # Make a request to list the lambda instances.
        response = self.client.get("/api/lambda-instances/")

        # Assert the structure of the response.
        self._assert_success_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(len(response.data['data']), number_of_lambda_instances)

        self._assert_success_request_response_content(response)

    # Test for listing lambda instances when there is no lambda instances created.
    def test_lambda_instances_list_empty(self):
        # Make a request to list the lambda_instances.
        response = self.client.get("/api/lambda-instances/")

        # Assert the structure of the response.
        self._assert_success_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(len(response.data['data']), 0)

        self._assert_success_request_response_content(response)

    # Test for listing lambda instances using pagination.
    def test_lambda_instances_list_pagination(self):
        # Create some lambda instances on the database.
        number_of_lambda_instances = randint(0, 100)
        for i in range(number_of_lambda_instances):
            LambdaInstance.objects.create(uuid=uuid.uuid4(), name="lambda_instance_{i}".format(i=i))

        # Make a request using both limit and offset parameters.
        limit = randint(0, 100)
        offset = randint(-100, 100)
        response = self.client.get("/api/lambda-instances/?limit={limit}&offset={offset}".
                                   format(limit=limit, offset=offset))

        # Assert the structure of the response.
        self._assert_success_request_response_structure(response)

        self.assertIn('pagination', response.data)

        # Assert the contents of the response.
        number_of_expected_lambda_instances = None
        if offset < 0:
            number_of_expected_lambda_instances = number_of_lambda_instances
        elif offset < number_of_lambda_instances:
            number_of_expected_lambda_instances = number_of_lambda_instances - offset
        else:
            number_of_expected_lambda_instances = 0

        if number_of_expected_lambda_instances >= limit:
            self.assertEqual(len(response.data['data']), limit)
        else:
            self.assertEqual(len(response.data['data']), number_of_expected_lambda_instances)

        if offset >= 0:
            self._assert_success_request_response_content(response, offset)
        else:
            self._assert_success_request_response_content(response)

    # Test for listing lambda instances when limit value for pagination is negative.
    def test_negative_pagination_limit(self):
        # Make a request to list the lambda instances.
        limit = randint(-100, -1)
        response = self.client.get("/api/lambda-instances/?limit={limit}".format(limit=limit))

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
        for lambda_instance in response.data['data']:
            self.assertIn('id', lambda_instance)
            self.assertIn('name', lambda_instance)

    def _assert_success_request_response_content(self, response, offset=0):
        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['lambda_instances_list'])

        for index, lambda_instance in enumerate(response.data['data']):
            self.assertEqual(lambda_instance['name'], "lambda_instance_{index}".
                             format(index=index + offset))
            self.assertRegexpMatches(lambda_instance['id'], r'^([^/.]+)$')
