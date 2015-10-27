import uuid
import mock
import json
import re

from random import randint, choice

from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import User, LambdaInstance, Server, PrivateNetwork
from backend.response_messages import ResponseMessages
from backend.exceptions import CustomParseError, CustomNotFoundError, CustomAlreadyDoneError,\
    CustomCantDoError


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
                          'instance_name': "Lambda Instance created from tests",
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
    @mock.patch('backend.views.get_vm_parameter_values', return_value={
        'vcpus': [1, 2, 4, 8],
        'ram': [512, 1024, 2048, 4096, 6144, 8192],
        'disk': [5, 10, 20, 40, 60, 80]
    })
    @mock.patch('backend.views.tasks.create_lambda_instance.delay',
                return_value=CeleryTaskResponse(uuid.uuid4()))
    def test_lambda_instance_create(self, mock_create_lambda_instance_task,
                                    mock_get_vm_parameter_values):
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
        mock_get_vm_parameter_values.assert_called_with(self.AUTHENTICATION_URL,
                                                        self.AUTHENTICATION_TOKEN)
        # Note: Can't user assert_called_with because the object provided to the mocked object is
        # created inside the view and cannot be reproduced here to be given as argument in
        # assert_called_with. That is why we test if the mocked object was called and if the data
        # of its first argument are equal to the data we provided.
        self.assertTrue(mock_create_lambda_instance_task.called)
        self.assertEqual(mock_create_lambda_instance_task.call_args[0][0].data,
                         json.loads(json.dumps(self.lambda_information)))

    # Test for request to create a lambda instance without providing each one of the mandatory
    # information.
    @mock.patch('backend.views.get_vm_parameter_values', return_value={
        'vcpus': [1, 2, 4, 8],
        'ram': [512, 1024, 2048, 4096, 6144, 8192],
        'disk': [5, 10, 20, 40, 60, 80]
    })
    def test_field_not_provided(self, mock_get_vm_parameter_values):
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
    @mock.patch('backend.views.get_vm_parameter_values', return_value={
        'vcpus': [1, 2, 4, 8],
        'ram': [512, 1024, 2048, 4096, 6144, 8192],
        'disk': [5, 10, 20, 40, 60, 80]
    })
    def test_no_field_provided(self, mock_get_vm_parameter_values):
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
    @mock.patch('backend.views.get_vm_parameter_values', return_value={
        'vcpus': [1, 2, 4, 8],
        'ram': [512, 1024, 2048, 4096, 6144, 8192],
        'disk': [5, 10, 20, 40, 60, 80]
    })
    def test_wrong_values(self, mock_get_vm_parameter_values):
        # Make a request to create a lambda instance.
        response = self.client.post("/api/lambda-instance/",
                                    {'project_name': "lambda.grnet.gr",
                                     'instance_name': "My Lambda Instance",
                                     'network_request': 1,
                                     'master_name': "lambda-master",
                                     'vcpus_master': -5,
                                     'vcpus_slave': -1,
                                     'ram_master': -4097,
                                     'ram_slave': -1000000,
                                     'disk_master': -21,
                                     'disk_slave': -33,
                                     'slaves': -2,
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
        self.assertEqual(len(response.data['errors']), 7)

        # Gather all the error messages in a list.
        error_messages = list()
        for error in response.data['errors']:
            self.assertEqual(error['status'], status.HTTP_400_BAD_REQUEST)
            error_messages.append(error['detail'][0])

        expected_error_messages_regular_expressions = [
            "^vcpus_master: Wrong Number of master vcpus,"
            " available choices \[([0-9]+, )+[0-9]+\]\.$",
            "^vcpus_slave: Wrong Number of slave vcpus, available choices \[([0-9]+, )+[0-9]+\]\.$",
            "^disk_master: Wrong Size of master disk, available choices \[([0-9]+, )+[0-9]+\]\.$",
            "^disk_slave: Wrong Size of slave disk, available choices \[([0-9]+, )+[0-9]+\]\.$",
            "^ram_master: Wrong Amount of master ram, available choices \[([0-9]+, )+[0-9]+\]\.$",
            "^ram_slave: Wrong Amount of slave ram, available choices \[([0-9]+, )+[0-9]+\]\.$",
            "^ip_allocation: Wrong choice for ip_allocation, available choices \['master'\]\.$"
        ]

        combined_regular_expressions = "(" + ")|(".\
            join(expected_error_messages_regular_expressions) + ")"

        for error_message in error_messages:
            self.assertIsNotNone(re.match(combined_regular_expressions, error_message))


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
        number_of_deleted_lambda_instances = randint(0, 20)
        for i in range(number_of_lambda_instances):
            LambdaInstance.objects.create(uuid=uuid.uuid4(),
                                          name="lambda_instance_{i}".format(i=i))
        for i in range(number_of_deleted_lambda_instances):
            LambdaInstance.objects.create(uuid=uuid.uuid4(),
                                          name="lambda_instance_{i}".format(i=i),
                                          status='6')

        # Make a request to list the lambda instances.
        response = self.client.get("/api/lambda-instances/")

        # Assert the structure of the response.
        self._assert_success_request_response_structure(response)

        # Assert the contents of the response.
        self.assertEqual(len(response.data['data']),
                         number_of_lambda_instances)

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
            self.assertIn('status', lambda_instance)

            self.assertIn('code', lambda_instance['status'])
            self.assertIn('message', lambda_instance['status'])
            self.assertIn('detail', lambda_instance['status'])

    def _assert_success_request_response_content(self, response, offset=0):
        # Assert the contents of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['lambda_instances_list'])

        # Gather all the returned lambda instance names and assert the id of each lambda instance.
        returned_lambda_instance_names = list()
        for lambda_instance in response.data['data']:
            returned_lambda_instance_names.append(lambda_instance['name'])
            self.assertRegexpMatches(lambda_instance['id'], r'^([^/.]+)$')

        # Gather all the expected lambda instance names.
        expected_lambda_instance_names = list()
        for index in range(len(response.data['data'])):
            expected_lambda_instance_names.append("lambda_instance_{}".format(index + offset))

        # Assert that every expected lambda instance name exists inside the returned lambda
        # instance names and that the sizes of these sets are equal.
        for expected_lambda_instance_name in expected_lambda_instance_names:
            self.assertIn(expected_lambda_instance_name, returned_lambda_instance_names)

        # Assert that the message, the code and the detail inside lambda instance status are
        # correctly chosen.
        for lambda_instance in response.data['data']:
            self.assertEqual(lambda_instance['status']['message'],
                             LambdaInstance.status_choices[
                                 int(lambda_instance['status']['code'])][1])
            self.assertEqual(lambda_instance['status']['detail'],
                             ResponseMessages.lambda_instance_status_details[
                                 lambda_instance['status']['message']])

        self.assertEqual(len(expected_lambda_instance_names), len(returned_lambda_instance_names))


class TestLambdaInstaceDetails(APITestCase):
    """
    Contains tests for lambda instance details API call.
    """

    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    instance_info = {
        "vcpus_master": 4,
        "project_name": "lambda.grnet.gr",
        "public_key_name": [
            "key-1",
            "key-2"
        ],
        "master_name": "lambda-master",
        "instance_name": "My Lambda Instance",
        "network_request": 1,
        "disk_slave": 20,
        "slaves": 2,
        "ram_slave": 4096,
        "ram_master": 4096,
        "vcpus_slave": 4,
        "ip_allocation": "master",
        "disk_master": 20
    }

    def setUp(self):
        # Create a user and force authenticate.
        self.user = User.objects.create(uuid=uuid.uuid4())
        self.client.force_authenticate(user=self.user)

        # Add a fake token to every request authentication header to be used by the API.
        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN))

        # Save a lambda instance on the database with a specified uuid.
        self.lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=self.lambda_instance_uuid,
                                                        name="Lambda Instance created from tests",
                                                        instance_info=json.dumps(
                                                            self.instance_info))

        # Save a server on the database.
        self.master_node_id = randint(2, 100)
        master_node = Server.objects.create(id=self.master_node_id, lambda_instance=lambda_instance)

        # Set the server as the master node for the lambda instance.
        lambda_instance.master_node = master_node
        lambda_instance.save()

    # Test for getting the details of a lambda instance.
    def test_lambda_instance_details(self):
        # Make a request to get the details of the lambda instance.
        response = self.client.get("/api/lambda-instances/{id}/".
                                   format(id=self.lambda_instance_uuid))

        # Assert the structure of the response.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('status', response.data)
        self.assertIn('data', response.data)

        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])

        self.assertEqual(len(response.data['data']), 1)
        self.assertIn('info', response.data['data'][0])
        self.assertIn('status', response.data['data'][0])
        self.assertIn('applications', response.data['data'][0])

        self.assertIn('id', response.data['data'][0]['info'])
        self.assertIn('name', response.data['data'][0]['info'])
        self.assertIn('instance_info', response.data['data'][0]['info'])

        self.assertIn('message', response.data['data'][0]['status'])
        self.assertIn('code', response.data['data'][0]['status'])
        self.assertIn('detail', response.data['data'][0]['status'])

        # Assert the content of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['lambda_instance_details'])

        self.assertEqual(len(response.data['data'][0]['applications']), 0)

        self.assertEqual(response.data['data'][0]['status']['code'], LambdaInstance.PENDING)
        self.assertEqual(response.data['data'][0]['status']['message'], "PENDING")
        self.assertEqual(response.data['data'][0]['status']['detail'],
                         ResponseMessages.lambda_instance_status_details["PENDING"])

        self.assertEqual(response.data['data'][0]['info']['id'],
                         "{id}".format(id=self.lambda_instance_uuid))
        self.assertEqual(response.data['data'][0]['info']['name'],
                         "Lambda Instance created from tests")
        extended_instance_info = self.instance_info
        extended_instance_info['master_node_id'] = self.master_node_id
        self.assertEqual(response.data['data'][0]['info']['instance_info'], extended_instance_info)

    # Test for getting the details of a lambda instance using the filter parameter with value
    # status.
    def test_details_filter_status(self):
        # Make a request to get the details of the lambda instance.
        response = self.client.get("/api/lambda-instances/{id}/?filter=status".
                                   format(id=self.lambda_instance_uuid))

        # Assert the structure of the response.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('status', response.data)
        self.assertIn('data', response.data)

        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])

        self.assertEqual(len(response.data['data']), 1)
        self.assertIn('id', response.data['data'][0])
        self.assertIn('name', response.data['data'][0])
        self.assertIn('status', response.data['data'][0])

        self.assertIn('message', response.data['data'][0]['status'])
        self.assertIn('code', response.data['data'][0]['status'])
        self.assertIn('detail', response.data['data'][0]['status'])

        # Assert the content of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['lambda_instance_details'])

        self.assertEqual(response.data['data'][0]['status']['code'], LambdaInstance.PENDING)
        self.assertEqual(response.data['data'][0]['status']['message'], "PENDING")
        self.assertEqual(response.data['data'][0]['status']['detail'],
                         ResponseMessages.lambda_instance_status_details["PENDING"])

        self.assertEqual(response.data['data'][0]['id'],
                         "{id}".format(id=self.lambda_instance_uuid))
        self.assertEqual(response.data['data'][0]['name'], "Lambda Instance created from tests")

    # Test for getting the details of a lambda instance using the filter parameter with value
    # info.
    def test_details_filter_info(self):
        # Make a request to get the details of the lambda instance.
        response = self.client.get("/api/lambda-instances/{id}/?filter=info".
                                   format(id=self.lambda_instance_uuid))

        # Assert the structure of the response.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('status', response.data)
        self.assertIn('data', response.data)

        self.assertIn('short_description', response.data['status'])
        self.assertIn('code', response.data['status'])

        self.assertEqual(len(response.data['data']), 1)
        self.assertIn('info', response.data['data'][0])

        self.assertIn('id', response.data['data'][0]['info'])
        self.assertIn('name', response.data['data'][0]['info'])
        self.assertIn('instance_info', response.data['data'][0]['info'])

        # Assert the content of the response.
        self.assertEqual(response.data['status']['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['lambda_instance_details'])

        self.assertEqual(response.data['data'][0]['info']['id'],
                         "{id}".format(id=self.lambda_instance_uuid))
        self.assertEqual(response.data['data'][0]['info']['name'],
                         "Lambda Instance created from tests")
        extended_instance_info = self.instance_info
        extended_instance_info['master_node_id'] = self.master_node_id
        self.assertEqual(response.data['data'][0]['info']['instance_info'], extended_instance_info)

    # Test for getting the details of a lambda instance using the filter parameter with a
    # wrong value.
    def test_details_filter_wrong(self):
        # Make a request to get the details of the lambda instance.
        response = self.client.get("/api/lambda-instances/{id}/?filter=wrong_value".
                                   format(id=self.lambda_instance_uuid))

        # Assert the structure of the response.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the content of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomParseError.messages['filter_value_error'])

    # Test for requesting the details of a lambda instance that doesn't exist.
    def test_non_existent_id(self):
        # Make a request to get the details of the lambda instance.
        response = self.client.get("/api/lambda-instances/{id}/".format(id=uuid.uuid4()))

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


class LambdaInstanceDestroy(APITestCase):
    """
    Contains tests for lambda instance destroy API call.
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

        # Save a lambda instance on the database with a specified uuid.
        self.lambda_instance_uuid = uuid.uuid4()
        self.lambda_instance = LambdaInstance.objects.\
            create(uuid=self.lambda_instance_uuid, name="Lambda Instance created from tests")

        # Save the servers of the lambda instance on the database.
        number_of_slaves = randint(2, 100)
        self.slaves = list()
        for slave_id in range(number_of_slaves):
            self.slaves.append(Server.objects.create(id=slave_id,
                                                     lambda_instance=self.lambda_instance))

        self.master_server = Server.objects.create(id=number_of_slaves + 1,
                                                   pub_ip="255.255.255.255", pub_ip_id=16343,
                                                   lambda_instance=self.lambda_instance)

        # Save the private network of the lambda instance on the database.
        self.private_network = PrivateNetwork.objects.create(id=number_of_slaves + 2,
                                                             gateway="192.168.0.1",
                                                             lambda_instance=self.lambda_instance)

    # Test for destroying a lambda instance.
    @mock.patch('backend.views.events.set_lambda_instance_status')
    @mock.patch('backend.views.tasks.lambda_instance_destroy')
    def test_lambda_instance_destroy(self, mock_lambda_instance_destroy_task,
                                     mock_set_lambda_instance_status_event):

        # Make a request to destroy the lambda instance.
        response = self.client.delete("/api/lambda-instances/{id}/".
                                      format(id=self.lambda_instance_uuid))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['lambda_instance_destroy'])

        # Gather the ids of the slaves.
        slave_ids = list()
        for slave in self.slaves:
            slave_ids.append(slave.id)

        # Assert that the proper tasks and views have been called.
        # A way to test the mock_lambda_instance_destroy_task call would be the following:
        # mock_lambda_instance_destroy_task.delay.\
        #     assert_called_with("{lambda_instance_id}".
        #                        format(lambda_instance_id=self.lambda_instance_uuid),
        #                        self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
        #                        self.master_server.id, slave_ids,
        #                        self.master_server.pub_ip_id, self.private_network.id)
        # but there is no guarantee about the sequence of the slave_ids that will be given
        # as input to the call.
        self.assertTrue(mock_lambda_instance_destroy_task.delay.called)
        self.assertEqual(mock_lambda_instance_destroy_task.delay.call_args[0][0],
                         "{}".format(self.lambda_instance_uuid))
        # self.assertEqual(mock_lambda_instance_destroy_task.delay.call_args[0][1],
        #                  self.AUTHENTICATION_URL)
        self.assertEqual(mock_lambda_instance_destroy_task.delay.call_args[0][1],
                         self.AUTHENTICATION_TOKEN)
        self.assertEqual(mock_lambda_instance_destroy_task.delay.call_args[0][2],
                         self.master_server.id)
        # Assert that every slave id was given to the task.
        slave_ids_on_call = mock_lambda_instance_destroy_task.delay.call_args[0][3]
        for slave_id in slave_ids:
            self.assertIn(slave_id, slave_ids_on_call)
        self.assertEqual(mock_lambda_instance_destroy_task.delay.call_args[0][4],
                         self.master_server.pub_ip_id)
        self.assertEqual(mock_lambda_instance_destroy_task.delay.call_args[0][5],
                         self.private_network.id)

        mock_set_lambda_instance_status_event.delay.\
            assert_called_with("{lambda_instance_id}".
                               format(lambda_instance_id=self.lambda_instance_uuid),
                               LambdaInstance.DESTROYING)

    # Test for destroying a lambda instance when the lambda instance doesn't exist.
    def test_non_existent_id(self):
        # Make a request to destroy the lambda instance.
        response = self.client.delete("/api/lambda-instances/{id}/".format(id=uuid.uuid4()))

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
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['lambda_instance_not_found'])

    # Test for destroying a lambda instance when it is already destroyed.
    def test_already_destroyed(self):

        # Change the status of the lambda instance to DESTROYED.
        self.lambda_instance.status = LambdaInstance.DESTROYED
        self.lambda_instance.save()

        # Make a request to destroy the lambda instance.
        response = self.client.delete("/api/lambda-instances/{id}/".
                                      format(id=self.lambda_instance_uuid))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomAlreadyDoneError.messages['lambda_instance_already'].
                         format(state="destroyed"))

    # Test for destroying a lambda instance when its status is CLUSTER_FAILED.
    def test_cluster_failed_status(self):

        # Change the status of the lambda instance to CLUSTER_FAILED.
        self.lambda_instance.status = LambdaInstance.CLUSTER_FAILED
        self.lambda_instance.save()

        # Make a request to destroy the lambda instance.
        response = self.client.delete("/api/lambda-instances/{id}/".
                                      format(id=self.lambda_instance_uuid))

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomCantDoError.messages['cant_do'].
                         format(action="destroy", object="a lambda instance",
                                status="CLUSTER_FAILED"))


class TestLambdaInstanceStart(APITestCase):
    """
    Contains tests for lambda instance start API calls.
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

        # Save a lambda instance on the database with a specified uuid.
        self.lambda_instance_uuid = uuid.uuid4()
        self.lambda_instance = LambdaInstance.objects.\
            create(uuid=self.lambda_instance_uuid, name="Lambda Instance created from tests",
                   status=LambdaInstance.STOPPED)

        # Save the servers of the lambda instance on the database.
        number_of_slaves = randint(2, 100)
        self.slaves = list()
        for slave_id in range(number_of_slaves):
            self.slaves.append(Server.objects.create(id=slave_id,
                                                     lambda_instance=self.lambda_instance))

        self.master_server = Server.objects.create(id=number_of_slaves + 1,
                                                   pub_ip="255.255.255.255", pub_ip_id=16343,
                                                   lambda_instance=self.lambda_instance)

    # Test for starting a lambda instance.
    @mock.patch('backend.views.events.set_lambda_instance_status')
    @mock.patch('backend.views.tasks.lambda_instance_start')
    def test_lambda_instance_start(self, mock_lambda_instance_start_task,
                                   mock_set_lambda_instance_status_event):

        # Make a request to start the lambda instance.
        response = self.client.post("/api/lambda-instances/{lambda_instance_id}/".
                                    format(lambda_instance_id=self.lambda_instance_uuid),
                                    {"action": "start"})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['lambda_instance_action'])

        # Gather the ids of the slaves.
        slave_ids = list()
        for slave in self.slaves:
            slave_ids.append(slave.id)

        # Assert that the proper tasks and views have been called.
        # A way to test the mock_lambda_instance_start_task call would be the following:
        # mock_lambda_instance_start_task.delay.\
        #     assert_called_with("{}".format(self.lambda_instance_uuid), self.AUTHENTICATION_URL,
        #                        self.AUTHENTICATION_TOKEN,
        #                        self.master_server.id, slave_ids)
        # but there is no guarantee about the sequence of the slave_ids that will be given
        # as input to the call.
        self.assertTrue(mock_lambda_instance_start_task.delay.called)
        self.assertEqual(mock_lambda_instance_start_task.delay.call_args[0][0],
                         "{}".format(self.lambda_instance_uuid))
        self.assertEqual(mock_lambda_instance_start_task.delay.call_args[0][1],
                         self.AUTHENTICATION_URL)
        self.assertEqual(mock_lambda_instance_start_task.delay.call_args[0][2],
                         self.AUTHENTICATION_TOKEN)
        self.assertEqual(mock_lambda_instance_start_task.delay.call_args[0][3],
                         self.master_server.id)
        # Assert that every slave id was given to the task.
        slave_ids_on_call = mock_lambda_instance_start_task.delay.call_args[0][4]
        for slave_id in slave_ids:
            self.assertIn(slave_id, slave_ids_on_call)

        mock_set_lambda_instance_status_event.delay.\
            assert_called_with("{}".format(self.lambda_instance_uuid), LambdaInstance.STARTING)

    # Test for starting a lambda instance when its status is FAILED.
    @mock.patch('backend.views.events.set_lambda_instance_status')
    @mock.patch('backend.views.tasks.lambda_instance_start')
    def test_lambda_instance_start_2(self, mock_lambda_instance_start_task,
                                     mock_set_lambda_instance_status_event):
        # Change the status of the lambda instance to FAILED.
        self.lambda_instance.status = LambdaInstance.FAILED
        self.lambda_instance.save()

        # Make a request to start the lambda instance.
        response = self.client.post("/api/lambda-instances/{lambda_instance_id}/".
                                    format(lambda_instance_id=self.lambda_instance_uuid),
                                    {"action": "start"})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['lambda_instance_action'])

        # Gather the ids of the slaves.
        slave_ids = list()
        for slave in self.slaves:
            slave_ids.append(slave.id)

        # Assert that the proper tasks and views have been called.
        # A way to test the mock_lambda_instance_start_task call would be the following:
        # mock_lambda_instance_start_task.delay.\
        #     assert_called_with("{}".format(self.lambda_instance_uuid), self.AUTHENTICATION_URL,
        #                        self.AUTHENTICATION_TOKEN,
        #                        self.master_server.id, slave_ids)
        # but there is no guarantee about the sequence of the slave_ids that will be given
        # as input to the call.
        self.assertTrue(mock_lambda_instance_start_task.delay.called)
        self.assertEqual(mock_lambda_instance_start_task.delay.call_args[0][0],
                         "{}".format(self.lambda_instance_uuid))
        self.assertEqual(mock_lambda_instance_start_task.delay.call_args[0][1],
                         self.AUTHENTICATION_URL)
        self.assertEqual(mock_lambda_instance_start_task.delay.call_args[0][2],
                         self.AUTHENTICATION_TOKEN)
        self.assertEqual(mock_lambda_instance_start_task.delay.call_args[0][3],
                         self.master_server.id)
        # Assert that every slave id was given to the task.
        slave_ids_on_call = mock_lambda_instance_start_task.delay.call_args[0][4]
        for slave_id in slave_ids:
            self.assertIn(slave_id, slave_ids_on_call)

        mock_set_lambda_instance_status_event.delay.\
            assert_called_with("{}".format(self.lambda_instance_uuid), LambdaInstance.STARTING)

    # Test for starting a lambda instance when the lambda instance doesn't exist.
    def test_non_existent_id(self):
        # Make a request to start the lambda instance.
        response = self.client.post("/api/lambda-instances/{}/".format(uuid.uuid4()),
                                    {"action": "start"})

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
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['lambda_instance_not_found'])

    # Test for starting a lambda instance when it is already started.
    def test_already_started(self):
        # Change the status of the lambda instance to started.
        self.lambda_instance.status = LambdaInstance.STARTED
        self.lambda_instance.save()

        # Make a request to start the lambda instance.
        response = self.client.post("/api/lambda-instances/{}/".format(self.lambda_instance_uuid),
                                    {"action": "start"})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomAlreadyDoneError.messages['lambda_instance_already'].
                         format(state="started"))

    # Test for starting the lambda instance when its status is not STARTED, STOPPED or FAILED.
    def test_other_status(self):
        # Change the status of the lambda instance to a random value except STARTED, STOPPED and
        # FAILED.
        values_list = [LambdaInstance.PENDING,
                       LambdaInstance.STARTING,
                       LambdaInstance.STOPPING,
                       LambdaInstance.DESTROYING,
                       LambdaInstance.DESTROYED,
                       LambdaInstance.SCALING_UP,
                       LambdaInstance.SCALING_DOWN,
                       LambdaInstance.CLUSTER_CREATED,
                       LambdaInstance.CLUSTER_FAILED,
                       LambdaInstance.INIT_DONE,
                       LambdaInstance.INIT_FAILED,
                       LambdaInstance.COMMONS_INSTALLED,
                       LambdaInstance.COMMONS_FAILED,
                       LambdaInstance.HADOOP_INSTALLED,
                       LambdaInstance.HADOOP_FAILED,
                       LambdaInstance.KAFKA_INSTALLED,
                       LambdaInstance.KAFKA_FAILED,
                       LambdaInstance.FLINK_INSTALLED,
                       LambdaInstance.FLINK_FAILED]

        self.lambda_instance.status = choice(values_list)
        self.lambda_instance.save()

        # Make a request to start the lambda instance.
        response = self.client.post("/api/lambda-instances/{}/".format(self.lambda_instance_uuid),
                                    {"action": "start"})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomCantDoError.messages['cant_do'].
                                        format(action="start", object="a lambda instance",
                                               status=LambdaInstance.status_choices[
                                                   int(self.lambda_instance.status)][1]))


class TestLambdaInstanceStop(APITestCase):
    """
    Contains tests for lambda instance stop API calls.
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

        # Save a lambda instance on the database with a specified uuid.
        self.lambda_instance_uuid = uuid.uuid4()
        self.lambda_instance = LambdaInstance.objects.\
            create(uuid=self.lambda_instance_uuid, name="Lambda Instance created from tests",
                   status=LambdaInstance.STARTED)

        # Save the servers of the lambda instance on the database.
        number_of_slaves = randint(2, 100)
        self.slaves = list()
        for slave_id in range(number_of_slaves):
            self.slaves.append(Server.objects.create(id=slave_id,
                                                     lambda_instance=self.lambda_instance))

        self.master_server = Server.objects.create(id=number_of_slaves + 1,
                                                   pub_ip="255.255.255.255", pub_ip_id=16343,
                                                   lambda_instance=self.lambda_instance)

    # Test for stopping a lambda instance.
    @mock.patch('backend.views.events.set_lambda_instance_status')
    @mock.patch('backend.views.tasks.lambda_instance_stop')
    def test_lambda_instance_stop(self, mock_lambda_instance_stop_task,
                                   mock_set_lambda_instance_status_event):

        # Make a request to stop the lambda instance.
        response = self.client.post("/api/lambda-instances/{lambda_instance_id}/".
                                    format(lambda_instance_id=self.lambda_instance_uuid),
                                    {"action": "stop"})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['lambda_instance_action'])

        # Gather the ids of the slaves.
        slave_ids = list()
        for slave in self.slaves:
            slave_ids.append(slave.id)

        # Assert that the proper tasks and views have been called.
        # A way to test the mock_lambda_instance_stop_task call would be the following:
        # mock_lambda_instance_stop_task.delay.\
        #     assert_called_with("{}".format(self.lambda_instance_uuid), self.AUTHENTICATION_URL,
        #                        self.AUTHENTICATION_TOKEN,
        #                        self.master_server.id, slave_ids)
        # but there is no guarantee about the sequence of the slave_ids that will be given
        # as input to the call.
        self.assertTrue(mock_lambda_instance_stop_task.delay.called)
        self.assertEqual(mock_lambda_instance_stop_task.delay.call_args[0][0],
                         "{}".format(self.lambda_instance_uuid))
        self.assertEqual(mock_lambda_instance_stop_task.delay.call_args[0][1],
                         self.AUTHENTICATION_URL)
        self.assertEqual(mock_lambda_instance_stop_task.delay.call_args[0][2],
                         self.AUTHENTICATION_TOKEN)
        self.assertEqual(mock_lambda_instance_stop_task.delay.call_args[0][3],
                         self.master_server.id)
        # Assert that every slave id was given to the task.
        slave_ids_on_call = mock_lambda_instance_stop_task.delay.call_args[0][4]
        for slave_id in slave_ids:
            self.assertIn(slave_id, slave_ids_on_call)

        mock_set_lambda_instance_status_event.delay.\
            assert_called_with("{}".format(self.lambda_instance_uuid), LambdaInstance.STOPPING)

    # Test for stopping a lambda instance when its status is FAILED.
    @mock.patch('backend.views.events.set_lambda_instance_status')
    @mock.patch('backend.views.tasks.lambda_instance_stop')
    def test_lambda_instance_stop_2(self, mock_lambda_instance_stop_task,
                                    mock_set_lambda_instance_status_event):
        # Change the status of the lambda instance to FAILED.
        self.lambda_instance.status = LambdaInstance.FAILED
        self.lambda_instance.save()

        # Make a request to stop the lambda instance.
        response = self.client.post("/api/lambda-instances/{lambda_instance_id}/".
                                    format(lambda_instance_id=self.lambda_instance_uuid),
                                    {"action": "stop"})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Assert the structure of the response.
        self.assertIn('status', response.data)

        self.assertIn('code', response.data['status'])
        self.assertIn('short_description', response.data['status'])

        # Assert the contents of the response
        self.assertEqual(response.data['status']['code'], status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status']['short_description'],
                         ResponseMessages.short_descriptions['lambda_instance_action'])

        # Gather the ids of the slaves.
        slave_ids = list()
        for slave in self.slaves:
            slave_ids.append(slave.id)

        # Assert that the proper tasks and views have been called.
        # A way to test the mock_lambda_instance_stop_task call would be the following:
        # mock_lambda_instance_stop_task.delay.\
        #     assert_called_with("{}".format(self.lambda_instance_uuid), self.AUTHENTICATION_URL,
        #                        self.AUTHENTICATION_TOKEN,
        #                        self.master_server.id, slave_ids)
        # but there is no guarantee about the sequence of the slave_ids that will be given
        # as input to the call.
        self.assertTrue(mock_lambda_instance_stop_task.delay.called)
        self.assertEqual(mock_lambda_instance_stop_task.delay.call_args[0][0],
                         "{}".format(self.lambda_instance_uuid))
        self.assertEqual(mock_lambda_instance_stop_task.delay.call_args[0][1],
                         self.AUTHENTICATION_URL)
        self.assertEqual(mock_lambda_instance_stop_task.delay.call_args[0][2],
                         self.AUTHENTICATION_TOKEN)
        self.assertEqual(mock_lambda_instance_stop_task.delay.call_args[0][3],
                         self.master_server.id)
        # Assert that every slave id was given to the task.
        slave_ids_on_call = mock_lambda_instance_stop_task.delay.call_args[0][4]
        for slave_id in slave_ids:
            self.assertIn(slave_id, slave_ids_on_call)

        mock_set_lambda_instance_status_event.delay.\
            assert_called_with("{}".format(self.lambda_instance_uuid), LambdaInstance.STOPPING)

    # Test for stopping a lambda instance when the lambda instance doesn't exist.
    def test_non_existent_id(self):
        # Make a request to stop the lambda instance.
        response = self.client.post("/api/lambda-instances/{}/".format(uuid.uuid4()),
                                    {"action": "stop"})

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
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomNotFoundError.messages['lambda_instance_not_found'])

    # Test for stopping a lambda instance when it is already stopped.
    def test_already_stopped(self):
        # Change the status of the lambda instance to stopped.
        self.lambda_instance.status = LambdaInstance.STOPPED
        self.lambda_instance.save()

        # Make a request to stop the lambda instance.
        response = self.client.post("/api/lambda-instances/{}/".format(self.lambda_instance_uuid),
                                    {"action": "stop"})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomAlreadyDoneError.messages['lambda_instance_already'].
                         format(state="stopped"))

    # Test for stopping the lambda instance when its status is not STARTED, STOPPED or FAILED.
    def test_other_status(self):
        # Change the status of the lambda instance to a random value except STARTED, STOPPED and
        # FAILED.
        values_list = [LambdaInstance.PENDING,
                       LambdaInstance.STARTING,
                       LambdaInstance.STOPPING,
                       LambdaInstance.DESTROYING,
                       LambdaInstance.DESTROYED,
                       LambdaInstance.SCALING_UP,
                       LambdaInstance.SCALING_DOWN,
                       LambdaInstance.CLUSTER_CREATED,
                       LambdaInstance.CLUSTER_FAILED,
                       LambdaInstance.INIT_DONE,
                       LambdaInstance.INIT_FAILED,
                       LambdaInstance.COMMONS_INSTALLED,
                       LambdaInstance.COMMONS_FAILED,
                       LambdaInstance.HADOOP_INSTALLED,
                       LambdaInstance.HADOOP_FAILED,
                       LambdaInstance.KAFKA_INSTALLED,
                       LambdaInstance.KAFKA_FAILED,
                       LambdaInstance.FLINK_INSTALLED,
                       LambdaInstance.FLINK_FAILED]

        self.lambda_instance.status = choice(values_list)
        self.lambda_instance.save()

        # Make a request to stop the lambda instance.
        response = self.client.post("/api/lambda-instances/{}/".format(self.lambda_instance_uuid),
                                    {"action": "stop"})

        # Assert the response code.
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Assert the structure of the response.
        self.assertIn('errors', response.data)

        self.assertEqual(len(response.data['errors']), 1)

        for error in response.data['errors']:
            self.assertIn('status', error)
            self.assertIn('detail', error)

        # Assert the contents of the response.
        self.assertEqual(response.data['errors'][0]['status'], status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomCantDoError.messages['cant_do'].
                                        format(action="stop", object="a lambda instance",
                                               status=LambdaInstance.status_choices[
                                                   int(self.lambda_instance.status)][1]))


class TestLambdaInstanceAction(APITestCase):
    """
    Contains tests for lambda instance action API calls.
    """

    def setUp(self):
        # Create a user and force authenticate.
        self.user = User.objects.create(uuid=uuid.uuid4())
        self.client.force_authenticate(user=self.user)

        # Save a lambda instance on the database with a specified uuid.
        self.lambda_instance_uuid = uuid.uuid4()
        self.lambda_instance = LambdaInstance.objects.\
            create(uuid=self.lambda_instance_uuid, name="Lambda Instance created from tests",
                   status=LambdaInstance.STOPPED)

    # Test for requesting an action that doesn't exist.
    def test_non_existent_action(self):
        # Make a request to perform a non existent action on the lambda instance.
        response = self.client.post("/api/lambda-instances/{}/".format(self.lambda_instance_uuid),
                                    {"action": "non-existent-action"})

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
        self.assertEqual(response.data['errors'][0]['detail'],
                         CustomParseError.messages['action_value_error'])
