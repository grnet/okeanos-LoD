from backend.models import User, LambdaInstance
from rest_framework.test import APITestCase
from rest_framework import status as rest_status

import uuid
from random import randint

class TestUsersAPI(APITestCase):
    AUTHENTICATION_TOKEN = "some_token"

    def setUp(self):
        self.authenticated_user = User.objects.create(uuid=uuid.uuid4())

        self.client.force_authenticate(user=self.authenticated_user)

        self.client.credentials(HTTP_AUTHORIZATION='Token {token}'.format(token=self.
                                                                          AUTHENTICATION_TOKEN))

        # create a number of users
        self.user_count = randint(1,20)
        created_users = []
        for i in range(self.user_count):
            created_users.append(User.objects.create(uuid=uuid.uuid4()))

        # crate a number of instances
        self.instances_count = randint(21,100)
        created_instances = []
        for i in range(self.instances_count):
            LambdaInstance.objects.create(uuid=uuid.uuid4(), instance_info="inst_info",
                                          owner=created_users[i%self.user_count],
                                          status=20)


    def tearDown(self):
        pass

    def test_users_count(self):
        """
        Tests API for correct count of the users owning at least one lambda instance.
        """

        expected_count = self.instances_count if self.instances_count<self.user_count else self.user_count

        response = self.client.get("/api/users/count", format='json')
        self.assertEqual(response.status_code, rest_status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['data']['count'], str(expected_count))