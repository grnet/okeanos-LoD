import uuid
import json

from rest_framework.test import APITestCase

from backend.models import User, LambdaInstance, Server, PrivateNetwork, Application,\
    LambdaInstanceApplicationConnection
from backend import events


class TestCeleryEvents(APITestCase):
    """
    Contains tests for Celery events.
    """

    def test_create_new_lambda_instance(self):
        instance_uuid = uuid.uuid4()
        instance_name = "A random name"
        specs = {"key-1": "value-1", "key-2": "value-2", "key-3": "value-3", "key-4": "value-4"}

        events.create_new_lambda_instance(instance_uuid, instance_name, json.dumps(specs))

        self.assertEqual(LambdaInstance.objects.all().count(), 1)

        lambda_instance = LambdaInstance.objects.all()[0]
        self.assertEqual(lambda_instance.uuid, instance_uuid)
        self.assertEqual(lambda_instance.name, instance_name)
        self.assertEqual(lambda_instance.instance_info, json.dumps(specs))

    def test_set_lambda_instance_status(self):
        # Save a lambda instance on the database.
        instance_uuid = uuid.uuid4()
        LambdaInstance.objects.create(uuid=instance_uuid)

        for status_choice in LambdaInstance.status_choices:
            status = status_choice[0]

            events.set_lambda_instance_status(instance_uuid, status)
            self.assertEqual(LambdaInstance.objects.get(uuid=instance_uuid).status, status)

        events.set_lambda_instance_status(instance_uuid, LambdaInstance.STARTED, "failure-message")
        self.assertEqual(LambdaInstance.objects.get(uuid=instance_uuid).failure_message,
                         "failure-message")

    def test_insert_cluster_info(self):
        # Create a lambda instance on the database.
        instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=instance_uuid)

        provisioner_response = {
            'nodes': {
                'master': {
                    'id': 0,
                    'internal_ip': "192.168.0.2"
                },
                'slaves': [
                    {'id': 1, 'internal_ip': "192.168.0.3"},
                    {'id': 2, 'internal_ip': "192.168.0.4"},
                    {'id': 3, 'internal_ip': "192.168.0.5"}
                ]
            },
            'vpn': {
                'id': 10
            },
            'subnet': {
                'cidr': "192.168.0.0/24",
                'gateway_ip': "192.168.0.1"
            },
            'ips': [
                {'id': 100, 'floating_ip_address': "255.255.255.255"}
            ]
        }
        specs = {
            'vcpus_master': 4,
            'vcpus_slave': 8,
            'ram_master': 4096,
            'ram_slave': 8192,
            'disk_master': 20,
            'disk_slave': 40
        }

        events.insert_cluster_info(instance_uuid, specs, provisioner_response)

        self.assertEqual(Server.objects.all().count(), 4)

        master_node = Server.objects.get(id=0)
        self.assertEqual(master_node.lambda_instance, lambda_instance)
        self.assertEqual(master_node.cpus, 4)
        self.assertEqual(master_node.ram, 4096)
        self.assertEqual(master_node.disk, 20)
        self.assertEqual(master_node.priv_ip, "192.168.0.2")
        self.assertEqual(master_node.pub_ip, "255.255.255.255")
        self.assertEqual(master_node.pub_ip_id, 100)

        lambda_instance.refresh_from_db()
        self.assertEqual(lambda_instance.master_node, master_node)

        slave_node_1 = Server.objects.get(id=1)
        self.assertEqual(slave_node_1.lambda_instance, lambda_instance)
        self.assertEqual(slave_node_1.cpus, 8)
        self.assertEqual(slave_node_1.ram, 8192)
        self.assertEqual(slave_node_1.disk, 40)
        self.assertEqual(slave_node_1.priv_ip, "192.168.0.3")

        slave_node_2 = Server.objects.get(id=2)
        self.assertEqual(slave_node_2.lambda_instance, lambda_instance)
        self.assertEqual(slave_node_2.cpus, 8)
        self.assertEqual(slave_node_2.ram, 8192)
        self.assertEqual(slave_node_2.disk, 40)
        self.assertEqual(slave_node_2.priv_ip, "192.168.0.4")

        slave_node_3 = Server.objects.get(id=3)
        self.assertEqual(slave_node_3.lambda_instance, lambda_instance)
        self.assertEqual(slave_node_3.cpus, 8)
        self.assertEqual(slave_node_3.ram, 8192)
        self.assertEqual(slave_node_3.disk, 40)
        self.assertEqual(slave_node_3.priv_ip, "192.168.0.5")

        private_network = PrivateNetwork.objects.get(id=10)
        self.assertEqual(private_network.lambda_instance, lambda_instance)
        self.assertEqual(private_network.subnet, "192.168.0.0/24")
        self.assertEqual(private_network.gateway, "192.168.0.1")

    def test_create_new_application(self):
        application_uuid = uuid.uuid4()
        application_name = "application.jar"
        application_path = "application_path"
        application_description = "application_description"
        application_type = "batch"
        application_owner = User.objects.create(uuid=uuid.uuid4())
        application_execution_environment_name = "Stream"

        events.create_new_application(application_uuid, application_name, application_path,
                                      application_description, application_type,
                                      application_owner, application_execution_environment_name)

        self.assertEqual(Application.objects.all().count(), 1)

        application = Application.objects.get(uuid=application_uuid)
        self.assertEqual(application.name, application_name)
        self.assertEqual(application.path, application_path)
        self.assertEqual(application.description, application_description)
        self.assertEqual(application.owner, application_owner)
        self.assertEqual(application.status, Application.UPLOADING)
        self.assertEqual(application.type, Application.BATCH)
        self.assertEqual(application.execution_environment_name,
                         application_execution_environment_name)

    def test_delete_application(self):
        # Create an application on the database.
        application_uuid = uuid.uuid4()
        Application.objects.create(uuid=application_uuid, type=Application.BATCH)

        # Assert that the application was created.
        self.assertEqual(Application.objects.all().count(), 1)

        events.delete_application(application_uuid)

        # Assert that the application was deleted.
        self.assertEqual(Application.objects.all().count(), 0)

    def test_set_application_status(self):
        # Save an application on the database.
        application_uuid = uuid.uuid4()
        Application.objects.create(uuid=application_uuid, type=Application.BATCH)

        for status_choice in Application.status_choices:
            status = status_choice[0]

            events.set_application_status(application_uuid, status)
            self.assertEqual(Application.objects.get(uuid=application_uuid).status, status)

        events.set_application_status(application_uuid, LambdaInstance.STARTED, "failure-message")
        self.assertEqual(Application.objects.get(uuid=application_uuid).failure_message,
                         "failure-message")

    def test_create_lambda_instance_application_connection(self):
        # Create a lambda instance on the database.
        lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=lambda_instance_uuid)

        # Create an application on the database.
        application_uuid = uuid.uuid4()
        application = Application.objects.create(uuid=application_uuid, type=Application.BATCH)

        events.create_lambda_instance_application_connection(lambda_instance_uuid, application_uuid)

        self.assertEqual(LambdaInstanceApplicationConnection.objects.all().count(), 1)

        LambdaInstanceApplicationConnection.objects.filter(lambda_instance=lambda_instance,
                                                           application=application).exists()

    def test_delete_lambda_instance_application_connection(self):
        # Create a lambda instance on the database.
        lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=lambda_instance_uuid)

        # Create an application on the database.
        application_uuid = uuid.uuid4()
        application = Application.objects.create(uuid=application_uuid, type=Application.BATCH)

        # Create a connection between the lambda instance and the application on the database.
        LambdaInstanceApplicationConnection.objects.create(lambda_instance=lambda_instance,
                                                           application=application)

        # Assert that the connection was created.
        self.assertEqual(LambdaInstanceApplicationConnection.objects.all().count(), 1)

        events.delete_lambda_instance_application_connection(lambda_instance_uuid, application_uuid)

        # Assert that the connection was deleted.
        self.assertEqual(LambdaInstanceApplicationConnection.objects.all().count(), 0)

    def test_start_batch_application(self):
        # Create a lambda instance on the database.
        lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=lambda_instance_uuid,
                                                        started_batch=False,
                                                        started_streaming=False)

        # Create an application on the database.
        application_uuid = uuid.uuid4()
        application = Application.objects.create(uuid=application_uuid, type=Application.BATCH)

        # Create a connection between the lambda instance and the application on the database.
        connection = LambdaInstanceApplicationConnection.objects.\
            create(lambda_instance=lambda_instance, application=application, started=False)

        events.start_stop_application(lambda_instance_uuid, application_uuid, 'start', 'batch')

        lambda_instance.refresh_from_db()
        connection.refresh_from_db()

        self.assertTrue(lambda_instance.started_batch)
        self.assertTrue(connection.started)

    def test_stop_batch_application(self):
        # Create a lambda instance on the database.
        lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=lambda_instance_uuid,
                                                        started_batch=True,
                                                        started_streaming=False)

        # Create an application on the database.
        application_uuid = uuid.uuid4()
        application = Application.objects.create(uuid=application_uuid, type=Application.BATCH)

        # Create a connection between the lambda instance and the application on the database.
        connection = LambdaInstanceApplicationConnection.objects.\
            create(lambda_instance=lambda_instance, application=application, started=True)

        events.start_stop_application(lambda_instance_uuid, application_uuid, 'stop', 'batch')

        lambda_instance.refresh_from_db()
        connection.refresh_from_db()

        self.assertFalse(lambda_instance.started_batch)
        self.assertFalse(connection.started)

    def test_start_streaming_application(self):
        # Create a lambda instance on the database.
        lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=lambda_instance_uuid,
                                                        started_batch=False,
                                                        started_streaming=False)

        # Create an application on the database.
        application_uuid = uuid.uuid4()
        application = Application.objects.create(uuid=application_uuid, type=Application.STREAMING)

        # Create a connection between the lambda instance and the application on the database.
        connection = LambdaInstanceApplicationConnection.objects.\
            create(lambda_instance=lambda_instance, application=application, started=False)

        events.start_stop_application(lambda_instance_uuid, application_uuid, 'start', 'streaming')

        lambda_instance.refresh_from_db()
        connection.refresh_from_db()

        self.assertTrue(lambda_instance.started_streaming)
        self.assertTrue(connection.started)

    def test_stop_streaming_application(self):
        # Create a lambda instance on the database.
        lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=lambda_instance_uuid,
                                                        started_batch=False,
                                                        started_streaming=True)

        # Create an application on the database.
        application_uuid = uuid.uuid4()
        application = Application.objects.create(uuid=application_uuid, type=Application.STREAMING)

        # Create a connection between the lambda instance and the application on the database.
        connection = LambdaInstanceApplicationConnection.objects.\
            create(lambda_instance=lambda_instance, application=application, started=True)

        events.start_stop_application(lambda_instance_uuid, application_uuid, 'stop', 'streaming')

        lambda_instance.refresh_from_db()
        connection.refresh_from_db()

        self.assertFalse(lambda_instance.started_streaming)
        self.assertFalse(connection.started)
