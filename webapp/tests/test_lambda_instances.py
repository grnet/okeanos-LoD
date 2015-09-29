import uuid
import mock
import json

from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import User
from backend.serializers import LambdaInstanceInfo
from backend.response_messages import ResponseMessages


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
    # project name
    project_name = "lambda.grnet.gr"
    # instance name
    instance_name = "My Lambda Instance"
    # network request
    network_request = 1
    # master name
    master_name = "lambda-master"
    # vcpus master
    vcpus_master = 4
    # vcpus slave
    vcpus_slave = 4
    # ram master
    ram_master = 4096
    # ram slave
    ram_slave = 4096
    # disk master
    disk_master = 20
    # disk slave
    disk_slave = 20
    # slaves
    slaves = 2
    # ip allocation
    ip_allocation = "master"
    # public key name
    public_key_name = ["key-1", "key-2"]

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
        lambda_information = {'project_name': self.project_name,
                              'instance_name': self.instance_name,
                              'network_request': self.network_request,
                              'master_name': self.master_name,
                              'vcpus_master': self.vcpus_master,
                              'vcpus_slave': self.vcpus_slave,
                              'ram_master': self.ram_master,
                              'ram_slave': self.ram_slave,
                              'disk_master': self.disk_master,
                              'disk_slave': self.disk_slave,
                              'slaves': self.slaves,
                              'ip_allocation': self.ip_allocation,
                              'public_key_name': self.public_key_name}

        response = self.client.post("/api/lambda-instance/", lambda_information, format='json')

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
                         json.loads(json.dumps(lambda_information)))
