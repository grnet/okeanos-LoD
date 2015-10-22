import mock
import uuid
import json

from rest_framework import status
from rest_framework.test import APITestCase

from backend import tasks
from backend.models import LambdaInstance, Application, Server


class CustomFile:
    """
    Class that emulates a file on the local file system.
    """

    def __init__(self):
        pass

    def close(self):
        pass


class CustomClientError(Exception):
    """
    Class that emulates kamaki ClientError exception.
    """

    def __init__(self, message, status=status.HTTP_200_OK):
        super(CustomClientError, self).__init__(message)

        self.status = status


class LambdaInfo:
    """
    Class that emulates the response of a validator.
    """

    def __init__(self, data):
        self.data = data


class TestCeleryTasks(APITestCase):
    """
    Contains tests for Celery tasks.
    """

    # Define ~okeanos authentication url.
    AUTHENTICATION_URL = "https://accounts.okeanos.grnet.gr/identity/v2.0"
    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.utils.lambda_instance_start')
    def test_lambda_instance_start(self, mock_lambda_instance_start_fokia,
                                   mock_set_lambda_instance_status_event,
                                   mock_set_lambda_instance_status_central_vm):
        lambda_instance_uuid = uuid.uuid4()
        master_id = 1
        slave_ids = [2, 3, 4]

        tasks.lambda_instance_start(lambda_instance_uuid, self.AUTHENTICATION_URL,
                                    self.AUTHENTICATION_TOKEN, master_id, slave_ids)

        mock_lambda_instance_start_fokia.assert_called_with(self.AUTHENTICATION_URL,
                                                            self.AUTHENTICATION_TOKEN,
                                                            master_id, slave_ids)
        mock_set_lambda_instance_status_event.delay.\
            assert_called_with(lambda_instance_uuid, LambdaInstance.STARTED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_called_with(self.AUTHENTICATION_TOKEN, lambda_instance_uuid,
                               LambdaInstance.STARTED, "")

    @mock.patch('backend.tasks.ClientError', new=CustomClientError)
    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.utils.lambda_instance_start')
    def test_lambda_instance_start_except(self, mock_lambda_instance_start_fokia,
                                          mock_set_lambda_instance_status_event,
                                          mock_set_lambda_instance_status_central_vm):
        # Fokia utils.lambda_instance_start will throw a CustomClientError exception when called.
        # ClientError exception is replaced with CustomClientError exception.
        mock_lambda_instance_start_fokia.side_effect = CustomClientError("exception-message")

        lambda_instance_uuid = uuid.uuid4()
        master_id = 1
        slave_ids = [2, 3, 4]

        tasks.lambda_instance_start(lambda_instance_uuid, self.AUTHENTICATION_URL,
                                    self.AUTHENTICATION_TOKEN, master_id, slave_ids)

        mock_lambda_instance_start_fokia.assert_called_with(self.AUTHENTICATION_URL,
                                                            self.AUTHENTICATION_TOKEN,
                                                            master_id, slave_ids)
        mock_set_lambda_instance_status_event.delay.\
            assert_called_with(lambda_instance_uuid, LambdaInstance.FAILED, "exception-message")
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_called_with(self.AUTHENTICATION_TOKEN, lambda_instance_uuid,
                               LambdaInstance.FAILED, "exception-message")

    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.utils.lambda_instance_stop')
    def test_lambda_instance_stop(self, mock_lambda_instance_stop_fokia,
                                  mock_set_lambda_instance_status_event,
                                  mock_set_lambda_instance_status_central_vm):
        lambda_instance_uuid = uuid.uuid4()
        master_id = 1
        slave_ids = [2, 3, 4]

        tasks.lambda_instance_stop(lambda_instance_uuid, self.AUTHENTICATION_URL,
                                   self.AUTHENTICATION_TOKEN, master_id, slave_ids)

        mock_lambda_instance_stop_fokia.assert_called_with(self.AUTHENTICATION_URL,
                                                           self.AUTHENTICATION_TOKEN,
                                                           master_id, slave_ids)
        mock_set_lambda_instance_status_event.delay.\
            assert_called_with(lambda_instance_uuid, LambdaInstance.STOPPED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_called_with(self.AUTHENTICATION_TOKEN, lambda_instance_uuid,
                               LambdaInstance.STOPPED, "")

    @mock.patch('backend.tasks.ClientError', new=CustomClientError)
    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.utils.lambda_instance_stop')
    def test_lambda_instance_stop_except(self, mock_lambda_instance_stop_fokia,
                                         mock_set_lambda_instance_status_event,
                                         set_lambda_instance_status_central_vm):
        # Fokia utils.lambda_instance_stop will throw a CustomClientError exception when called.
        # ClientError exception is replaced with CustomClientError exception.
        mock_lambda_instance_stop_fokia.side_effect = CustomClientError("exception-message")

        lambda_instance_uuid = uuid.uuid4()
        master_id = 1
        slave_ids = [2, 3, 4]

        tasks.lambda_instance_stop(lambda_instance_uuid, self.AUTHENTICATION_URL,
                                   self.AUTHENTICATION_TOKEN, master_id, slave_ids)

        mock_lambda_instance_stop_fokia.assert_called_with(self.AUTHENTICATION_URL,
                                                           self.AUTHENTICATION_TOKEN,
                                                           master_id, slave_ids)
        mock_set_lambda_instance_status_event.delay.\
            assert_called_with(lambda_instance_uuid, LambdaInstance.FAILED, "exception-message")
        set_lambda_instance_status_central_vm.delay.\
            assert_called_with(self.AUTHENTICATION_TOKEN, lambda_instance_uuid,
                               LambdaInstance.FAILED, "exception-message")

    @mock.patch('backend.central_vm_tasks.delete_lambda_instance_central_vm')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.lambda_instance_manager.lambda_instance_destroy')
    def test_lambda_instance_destroy(self, mock_lambda_instance_destroy_fokia,
                                     mock_set_lambda_instance_status_event,
                                     mock_delete_lambda_instance_central_vm):
        lambda_instance_uuid = uuid.uuid4()
        master_id = 1
        slave_ids = [2, 3, 4]
        public_ip_id = 10
        private_network_id = 100

        tasks.lambda_instance_destroy(lambda_instance_uuid, self.AUTHENTICATION_TOKEN, master_id,
                                      slave_ids, public_ip_id, private_network_id)

        mock_lambda_instance_destroy_fokia.assert_called_with(lambda_instance_uuid,
                                                              self.AUTHENTICATION_TOKEN,
                                                              master_id, slave_ids,
                                                              public_ip_id, private_network_id)
        mock_set_lambda_instance_status_event.delay.\
            assert_called_with(lambda_instance_uuid, LambdaInstance.DESTROYED)
        mock_delete_lambda_instance_central_vm.delay.\
            assert_called_with(self.AUTHENTICATION_TOKEN, lambda_instance_uuid)

    @mock.patch('backend.tasks.ClientError', new=CustomClientError)
    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.lambda_instance_manager.lambda_instance_destroy')
    def test_lambda_instance_destroy_except(self, mock_lambda_instance_destroy_fokia,
                                            mock_set_lambda_instance_status_event,
                                            mock_set_lambda_instance_status_central_vm):
        mock_lambda_instance_destroy_fokia.side_effect = CustomClientError("exception-message")

        lambda_instance_uuid = uuid.uuid4()
        master_id = 1
        slave_ids = [2, 3, 4]
        public_ip_id = 10
        private_network_id = 100

        tasks.lambda_instance_destroy(lambda_instance_uuid, self.AUTHENTICATION_TOKEN, master_id,
                                      slave_ids, public_ip_id, private_network_id)

        mock_lambda_instance_destroy_fokia.assert_called_with(lambda_instance_uuid,
                                                              self.AUTHENTICATION_TOKEN,
                                                              master_id, slave_ids,
                                                              public_ip_id, private_network_id)
        mock_set_lambda_instance_status_event.delay.\
            assert_called_with(lambda_instance_uuid, LambdaInstance.FAILED, "exception-message")
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_called_with(self.AUTHENTICATION_TOKEN, lambda_instance_uuid,
                               LambdaInstance.FAILED, "exception-message")

    @mock.patch('backend.central_vm_tasks.create_application_central_vm')
    @mock.patch('backend.tasks.remove')
    @mock.patch('__builtin__.open')
    @mock.patch('backend.tasks.events.set_application_status')
    @mock.patch('backend.tasks.utils.upload_file_to_pithos')
    def test_upload_application_to_pithos(self, mock_upload_file_to_pithos_fokia,
                                          mock_set_application_status_event, mock_builtin_open,
                                          mock_os_remove,
                                          mock_create_application_central_vm):
        # Create the database entry of the Application.
        application_name = "application_name"
        application_description = "application_description"
        container_name = "container_name"
        project_name = "project_name"
        local_file_path = "local_file_path"
        application_uuid = uuid.uuid4()

        Application.objects.create(uuid=application_uuid, name=application_name,
                                   path=container_name, description=application_description,
                                   type=Application.BATCH)

        mock_local_file = mock.create_autospec(CustomFile())
        mock_builtin_open.return_value = mock_local_file

        tasks.upload_application_to_pithos(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                                           container_name, project_name, local_file_path,
                                           application_uuid)

        mock_builtin_open.assert_called_with(local_file_path, 'r')
        mock_upload_file_to_pithos_fokia.assert_called_with(self.AUTHENTICATION_URL,
                                                            self.AUTHENTICATION_TOKEN,
                                                            container_name, project_name,
                                                            mock_local_file)
        mock_set_application_status_event.delay.\
            assert_called_with(application_uuid=application_uuid, status=Application.UPLOADED)
        mock_create_application_central_vm.delay.\
            assert_called_with(self.AUTHENTICATION_TOKEN, application_uuid, application_name,
                               application_description)
        self.assertTrue(mock_local_file.close.called)
        mock_os_remove.assert_called_with(local_file_path)

    @mock.patch('backend.tasks.ClientError', new=CustomClientError)
    @mock.patch('backend.tasks.remove')
    @mock.patch('__builtin__.open')
    @mock.patch('backend.tasks.events.set_application_status')
    @mock.patch('backend.tasks.utils.upload_file_to_pithos')
    def test_upload_application_to_pithos_except(self, mock_upload_file_to_pithos_fokia,
                                                 mock_set_application_status_event,
                                                 mock_builtin_open, mock_os_remove):
        mock_upload_file_to_pithos_fokia.side_effect = CustomClientError("exception-message")

        container_name = "container_name"
        project_name = "project_name"
        local_file_path = "local_file_path"
        application_uuid = uuid.uuid4()

        mock_local_file = mock.create_autospec(CustomFile())
        mock_builtin_open.return_value = mock_local_file

        tasks.upload_application_to_pithos(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                                           container_name, project_name, local_file_path,
                                           application_uuid)

        mock_builtin_open.assert_called_with(local_file_path, 'r')
        mock_upload_file_to_pithos_fokia.assert_called_with(self.AUTHENTICATION_URL,
                                                            self.AUTHENTICATION_TOKEN,
                                                            container_name, project_name,
                                                            mock_local_file)
        mock_set_application_status_event.delay.\
            assert_called_with(application_uuid, Application.FAILED, "exception-message")
        self.assertTrue(mock_local_file.close.called)
        mock_os_remove.assert_called_with(local_file_path)

    @mock.patch('backend.central_vm_tasks.delete_application_central_vm')
    @mock.patch('backend.tasks.events.delete_application')
    @mock.patch('backend.tasks.utils.delete_file_from_pithos')
    def test_delete_application_from_pithos(self, mock_delete_file_from_pithos_fokia,
                                            mock_delete_application_event,
                                            mock_delete_application_central_vm):
        container_name = "container_name"
        filename = "filename"
        application_uuid = uuid.uuid4()

        tasks.delete_application_from_pithos(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                                             container_name, filename, application_uuid)

        mock_delete_file_from_pithos_fokia.assert_called_with(self.AUTHENTICATION_URL,
                                                              self.AUTHENTICATION_TOKEN,
                                                              container_name, filename)
        mock_delete_application_event.delay.assert_called_with(application_uuid)
        mock_delete_application_central_vm.delay.\
            assert_called_with(self.AUTHENTICATION_TOKEN, application_uuid)

    @mock.patch('backend.tasks.ClientError', new=CustomClientError)
    @mock.patch('backend.central_vm_tasks.set_application_status_central_vm')
    @mock.patch('backend.tasks.events.set_application_status')
    @mock.patch('backend.tasks.utils.delete_file_from_pithos')
    def test_delete_application_from_pithos_except(self, mock_delete_file_from_pithos_fokia,
                                                   mock_set_application_status_event,
                                                   mock_set_application_status_central_vm):
        mock_delete_file_from_pithos_fokia.side_effect = CustomClientError("exception-message")

        container_name = "container_name"
        filename = "filename"
        application_uuid = uuid.uuid4()

        tasks.delete_application_from_pithos(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                                             container_name, filename, application_uuid)

        mock_delete_file_from_pithos_fokia.assert_called_with(self.AUTHENTICATION_URL,
                                                              self.AUTHENTICATION_TOKEN,
                                                              container_name, filename)
        mock_set_application_status_event.delay.\
            assert_called_with(application_uuid, Application.FAILED, "exception-message")
        mock_set_application_status_central_vm.delay.\
            assert_called_with(self.AUTHENTICATION_TOKEN, application_uuid,
                               Application.FAILED, "exception-message")

    @mock.patch('backend.tasks.ClientError', new=CustomClientError)
    @mock.patch('backend.central_vm_tasks.delete_application_central_vm')
    @mock.patch('backend.tasks.events.delete_application')
    @mock.patch('backend.tasks.utils.delete_file_from_pithos')
    def test_delete_application_from_pithos_except_404(self, mock_delete_file_from_pithos_fokia,
                                                       mock_delete_application_event,
                                                       mock_delete_application_central_vm):
        mock_delete_file_from_pithos_fokia.\
            side_effect = CustomClientError("exception-message", status.HTTP_404_NOT_FOUND)

        container_name = "container_name"
        filename = "filename"
        application_uuid = uuid.uuid4()

        tasks.delete_application_from_pithos(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                                             container_name, filename, application_uuid)

        mock_delete_file_from_pithos_fokia.assert_called_with(self.AUTHENTICATION_URL,
                                                              self.AUTHENTICATION_TOKEN,
                                                              container_name, filename)
        mock_delete_application_event.delay.assert_called_with(application_uuid)
        mock_delete_application_central_vm.delay.\
            assert_called_with(self.AUTHENTICATION_TOKEN, application_uuid)

    @mock.patch('backend.tasks.events.create_lambda_instance_application_connection')
    @mock.patch('backend.tasks.remove')
    @mock.patch('backend.tasks.system')
    @mock.patch('backend.tasks.path.exists', return_value=True)
    @mock.patch('__builtin__.open')
    @mock.patch('backend.tasks.utils.download_file_from_pithos')
    def test_deploy_application(self, mock_download_file_from_pithos_fokia, mock_builtin_open,
                                mock_path_exists, mock_system, mock_remove,
                                mock_create_lambda_instance_application_connection_event):
        container_name = "container_name"

        lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=lambda_instance_uuid)

        master_node = Server.objects.create(id=10, lambda_instance=lambda_instance)
        lambda_instance.master_node = master_node
        lambda_instance.save()

        application_uuid = uuid.uuid4()
        Application.objects.create(uuid=application_uuid, name="application.jar",
                                   type=Application.BATCH)

        mock_local_file = mock.create_autospec(CustomFile())
        mock_builtin_open.return_value = mock_local_file

        # Make a call to deploy the application.
        tasks.deploy_application(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                                 container_name, lambda_instance_uuid, application_uuid)

        # Assert that the proper mocks have been called.
        mock_path_exists.assert_called_with("/tmp/lambda_applications")
        mock_builtin_open.assert_called_with("/tmp/lambda_applications/application.jar", 'w+')
        mock_download_file_from_pithos_fokia.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               container_name, "application.jar", mock_local_file)
        self.assertTrue(mock_local_file.close.called)
        mock_system.assert_called_with("scp /tmp/lambda_applications/application.jar "
                                          "root@snf-10.vm.okeanos.grnet.gr:/home/flink/")
        mock_remove.assert_called_with("/tmp/lambda_applications/application.jar")
        mock_create_lambda_instance_application_connection_event.delay.\
            assert_called_with(lambda_instance_uuid, application_uuid)

    @mock.patch('backend.tasks.ClientError', new=CustomClientError)
    @mock.patch('backend.central_vm_tasks.set_application_status_central_vm')
    @mock.patch('backend.tasks.path.exists', return_value=False)
    @mock.patch('backend.tasks.mkdir')
    @mock.patch('__builtin__.open')
    @mock.patch('backend.tasks.events.set_application_status')
    @mock.patch('backend.tasks.utils.download_file_from_pithos')
    def test_deploy_application_except(self, mock_download_file_from_pithos_fokia,
                                       mock_set_application_status_event, mock_builtin_open,
                                       mock_mkdir, mock_path_exists,
                                       mock_set_application_status_central_vm):
        mock_download_file_from_pithos_fokia.side_effect = CustomClientError("exception-message")

        container_name = "container_name"

        lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=lambda_instance_uuid)

        master_node = Server.objects.create(id=10, lambda_instance=lambda_instance)
        lambda_instance.master_node = master_node
        lambda_instance.save()

        application_uuid = uuid.uuid4()
        Application.objects.create(uuid=application_uuid, name="application.jar",
                                   type=Application.BATCH)

        mock_local_file = mock.create_autospec(CustomFile())
        mock_builtin_open.return_value = mock_local_file

        # Make a call to deploy the application.
        tasks.deploy_application(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                                 container_name, lambda_instance_uuid, application_uuid)

        # Assert that the proper mocks have been called.
        mock_path_exists.assert_called_with("/tmp/lambda_applications")
        mock_mkdir.assert_called_with("/tmp/lambda_applications")
        mock_builtin_open.assert_called_with("/tmp/lambda_applications/application.jar", 'w+')
        mock_download_file_from_pithos_fokia.\
            assert_called_with(self.AUTHENTICATION_URL, self.AUTHENTICATION_TOKEN,
                               container_name, "application.jar", mock_local_file)
        mock_set_application_status_event.delay.\
            assert_called_with(application_uuid, Application.FAILED, "exception-message")
        mock_set_application_status_central_vm.delay.\
            assert_called_with(self.AUTHENTICATION_TOKEN, application_uuid, Application.FAILED,
                               "exception-message")
        self.assertTrue(mock_local_file.close.called)

    @mock.patch('backend.tasks.system')
    @mock.patch('backend.tasks.events.delete_lambda_instance_application_connection')
    def test_withdraw_application(self, mock_delete_lambda_instance_application_connection_event,
                                  mock_system):
        # Create a lambda instance on the database.
        lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=lambda_instance_uuid)

        # Create a server on the database.
        master_node = Server.objects.create(id=10, lambda_instance=lambda_instance)
        lambda_instance.master_node = master_node
        lambda_instance.save()

        # Create an application on the database.
        application_uuid = uuid.uuid4()
        Application.objects.create(uuid=application_uuid, name="application.jar",
                                   type=Application.BATCH)

        tasks.withdraw_application(lambda_instance_uuid, application_uuid)

        # Assert that the proper mocks have been called.
        mock_system.assert_called_with("ssh -l root snf-10.vm.okeanos.grnet.gr "
                                       "rm /home/flink/application.jar")
        mock_delete_lambda_instance_application_connection_event.delay.\
            assert_called_with(lambda_instance_uuid, application_uuid)

    @mock.patch('backend.tasks.events.start_stop_application')
    @mock.patch('backend.tasks.lambda_instance_manager', return_value={})
    @mock.patch('backend.tasks._check_ansible_result', return_value="Ansible successful")
    @mock.patch('backend.tasks.Manager', autospec=True)
    def test_start_stop_application(self, mock_manager_fokia, mock_check_ansible_result,
                                    mock_lambda_instance_manager_fokia,
                                    mock_start_stop_application_event):
        # Create a lambda instance on the database.
        lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=lambda_instance_uuid)

        # Create a server on the database.
        master_node = Server.objects.create(id=10, lambda_instance=lambda_instance)
        lambda_instance.master_node = master_node
        lambda_instance.save()

        # Create an application on the database.
        application_uuid = uuid.uuid4()
        Application.objects.create(uuid=application_uuid, name="application.jar",
                                   type=Application.BATCH)

        # Setup mock return values and side effects.
        mock_ansible_manager = mock.Mock()
        mock_manager_fokia.return_value = mock_ansible_manager

        mock_ansible_result = mock.Mock()
        mock_lambda_instance_manager_fokia.run_playbook.return_value = mock_ansible_result

        # Make a call to start the application.
        tasks.start_stop_application(lambda_instance_uuid, application_uuid, 'start', 'batch',
                                     'application.jar')

        # Assert that the proper mocks have been called.
        mock_manager_fokia.assert_called_with({
            'nodes': {
                'master': {
                    'id': 10,
                    'internal_ip': None
                }
            }
        })
        mock_ansible_manager.create_master_inventory.\
            assert_called_with(app_action="start", app_type="batch",
                                            jar_filename="application.jar")
        mock_lambda_instance_manager_fokia.run_playbook.\
            assert_called_with(mock_ansible_manager, "flink-apps.yml")
        mock_check_ansible_result.assert_called_with(mock_ansible_result)
        mock_start_stop_application_event.delay.\
            assert_called_with(lambda_instance_uuid=lambda_instance_uuid,
                               application_uuid=application_uuid, action="start",
                               app_type="batch")

    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.central_vm_tasks.create_lambda_instance_central_vm')
    @mock.patch('backend.tasks._check_ansible_result', return_value="Ansible successful")
    @mock.patch('backend.tasks.get_named_keys', return_value={'key-1': "ssh", 'key-2': "ssh2"})
    @mock.patch('backend.tasks.lambda_instance_manager')
    @mock.patch('backend.tasks.events.insert_cluster_info')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.events.create_new_lambda_instance')
    def test_create_lambda_instance(self, mock_create_new_lambda_instance_event,
                                    mock_set_lambda_instance_status_event,
                                    mock_insert_cluster_info_event,
                                    mock_lambda_instance_manager_fokia,
                                    mock_get_named_keys, mock_check_ansible_result,
                                    mock_create_lambda_instance_central_vm,
                                    mock_set_lambda_instance_status_central_vm):
        # Setup mock return values and side effects.
        mock_ansible_manager = mock.Mock()
        mock_provisioner_response = mock.Mock()

        mock_lambda_instance_manager_fokia.create_cluster.return_value = mock_ansible_manager,\
                                                                         mock_provisioner_response

        mock_ansible_result = mock.Mock()
        mock_lambda_instance_manager_fokia.run_playbook.return_value = mock_ansible_result

        # Create the input that will be given to the task.
        specs = {
            'instance_name': "Lambda Instance created from Tests",
            'public_key_name': ['key-1', 'key-2'],
            'master_name': "master_name",
            'slaves': 2,
            'vcpus_master': 4,
            'vcpus_slave': 8,
            'ram_master': 4096,
            'ram_slave': 8192,
            'disk_master': 20,
            'disk_slave': 40,
            'ip_allocation': 'master',
            'network_request': 1,
            'project_name': "lambda.grnet.gr"
        }
        lambda_info = LambdaInfo(specs)

        # Call create lambda instance task.
        tasks.create_lambda_instance(lambda_info, self.AUTHENTICATION_TOKEN)

        # Assert that the proper mocks have been called.
        mock_create_new_lambda_instance_event.delay.\
            assert_called_with(instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_create_lambda_instance_central_vm.delay.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_get_named_keys.assert_called_with(self.AUTHENTICATION_TOKEN,
                                               names=['key-1', 'key-2'])
        mock_lambda_instance_manager_fokia.create_cluster.\
            assert_called_with(cluster_id=None,
                               auth_token=self.AUTHENTICATION_TOKEN, master_name="master_name",
                               slaves=2, vcpus_master=4, vcpus_slave=8, ram_master=4096,
                               ram_slave=8192, disk_master=20, disk_slave=40,
                               ip_allocation="master", network_request=1,
                               project_name="lambda.grnet.gr",
                               pub_keys={'key-1': "ssh", 'key-2': "ssh2"})
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.CLUSTER_CREATED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.CLUSTER_CREATED, "")
        mock_insert_cluster_info_event.delay.\
            assert_called_with(instance_uuid=None, provisioner_response=mock_provisioner_response,
                               specs=specs)

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'initialize.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.INIT_DONE)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.INIT_DONE, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'common-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.COMMONS_INSTALLED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.COMMONS_INSTALLED, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'hadoop-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.HADOOP_INSTALLED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.HADOOP_INSTALLED, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'kafka-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.KAFKA_INSTALLED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.KAFKA_INSTALLED, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'flink-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.FLINK_INSTALLED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.FLINK_INSTALLED, "")

        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.STARTED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.STARTED, "")

    @mock.patch('backend.tasks.ClientError', new=CustomClientError)
    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.central_vm_tasks.create_lambda_instance_central_vm')
    @mock.patch('backend.tasks.get_named_keys', return_value={'key-1': "ssh", 'key-2': "ssh2"})
    @mock.patch('backend.tasks.lambda_instance_manager')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.events.create_new_lambda_instance')
    def test_create_lambda_instance_except(self, mock_create_new_lambda_instance_event,
                                           mock_set_lambda_instance_status_event,
                                           mock_lambda_instance_manager_fokia,
                                           mock_get_named_keys,
                                           mock_create_lambda_instance_central_vm,
                                           mock_set_lambda_instance_status_central_vm):
        # Setup mock return values and side effects.
        mock_lambda_instance_manager_fokia.create_cluster.\
            side_effect = CustomClientError("exception-message")

        # Create the input that will be given to the task.
        specs = {
            'instance_name': "Lambda Instance created from Tests",
            'public_key_name': ['key-1', 'key-2'],
            'master_name': "master_name",
            'slaves': 2,
            'vcpus_master': 4,
            'vcpus_slave': 8,
            'ram_master': 4096,
            'ram_slave': 8192,
            'disk_master': 20,
            'disk_slave': 40,
            'ip_allocation': 'master',
            'network_request': 1,
            'project_name': "lambda.grnet.gr"
        }
        lambda_info = LambdaInfo(specs)

        # Call create lambda instance task.
        tasks.create_lambda_instance(lambda_info, self.AUTHENTICATION_TOKEN)

        # Assert that the proper mocks have been called.
        mock_create_new_lambda_instance_event.delay.\
            assert_called_with(instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_create_lambda_instance_central_vm.delay.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_get_named_keys.assert_called_with(self.AUTHENTICATION_TOKEN,
                                               names=['key-1', 'key-2'])
        mock_lambda_instance_manager_fokia.create_cluster.\
            assert_called_with(cluster_id=None,
                               auth_token=self.AUTHENTICATION_TOKEN, master_name="master_name",
                               slaves=2, vcpus_master=4, vcpus_slave=8, ram_master=4096,
                               ram_slave=8192, disk_master=20, disk_slave=40,
                               ip_allocation="master", network_request=1,
                               project_name="lambda.grnet.gr",
                               pub_keys={'key-1': "ssh", 'key-2': "ssh2"})
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.CLUSTER_FAILED,
                            failure_message="exception-message")
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.CLUSTER_FAILED,
                            "exception-message")

    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.central_vm_tasks.create_lambda_instance_central_vm')
    @mock.patch('backend.tasks._check_ansible_result')
    @mock.patch('backend.tasks.get_named_keys', return_value={'key-1': "ssh", 'key-2': "ssh2"})
    @mock.patch('backend.tasks.lambda_instance_manager')
    @mock.patch('backend.tasks.events.insert_cluster_info')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.events.create_new_lambda_instance')
    def test_create_lambda_instance_init_fail(self, mock_create_new_lambda_instance_event,
                                              mock_set_lambda_instance_status_event,
                                              mock_insert_cluster_info_event,
                                              mock_lambda_instance_manager_fokia,
                                              mock_get_named_keys, mock_check_ansible_result,
                                              mock_create_lambda_instance_central_vm,
                                              mock_set_lambda_instance_status_central_vm):
        # Setup mock return values and side effects.
        mock_ansible_manager = mock.Mock()
        mock_provisioner_response = mock.Mock()

        mock_lambda_instance_manager_fokia.create_cluster.return_value = mock_ansible_manager,\
                                                                         mock_provisioner_response

        mock_ansible_result = mock.Mock()
        mock_lambda_instance_manager_fokia.run_playbook.return_value = mock_ansible_result

        mock_check_ansible_result.side_effect = ["Ansible task failed"]
        # Create the input that will be given to the task.
        specs = {
            'instance_name': "Lambda Instance created from Tests",
            'public_key_name': ['key-1', 'key-2'],
            'master_name': "master_name",
            'slaves': 2,
            'vcpus_master': 4,
            'vcpus_slave': 8,
            'ram_master': 4096,
            'ram_slave': 8192,
            'disk_master': 20,
            'disk_slave': 40,
            'ip_allocation': 'master',
            'network_request': 1,
            'project_name': "lambda.grnet.gr"
        }
        lambda_info = LambdaInfo(specs)

        # Call create lambda instance task.
        tasks.create_lambda_instance(lambda_info, self.AUTHENTICATION_TOKEN)

        # Assert that the proper mocks have been called.
        mock_create_new_lambda_instance_event.delay.\
            assert_called_with(instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_create_lambda_instance_central_vm.delay.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_get_named_keys.assert_called_with(self.AUTHENTICATION_TOKEN,
                                               names=['key-1', 'key-2'])
        mock_lambda_instance_manager_fokia.create_cluster.\
            assert_called_with(cluster_id=None,
                               auth_token=self.AUTHENTICATION_TOKEN, master_name="master_name",
                               slaves=2, vcpus_master=4, vcpus_slave=8, ram_master=4096,
                               ram_slave=8192, disk_master=20, disk_slave=40,
                               ip_allocation="master", network_request=1,
                               project_name="lambda.grnet.gr",
                               pub_keys={'key-1': "ssh", 'key-2': "ssh2"})
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.CLUSTER_CREATED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.CLUSTER_CREATED, "")
        mock_insert_cluster_info_event.delay.\
            assert_called_with(instance_uuid=None, provisioner_response=mock_provisioner_response,
                               specs=specs)

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'initialize.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.INIT_FAILED,
                            failure_message="Ansible task failed")
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.INIT_FAILED,
                            "Ansible task failed")

    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.central_vm_tasks.create_lambda_instance_central_vm')
    @mock.patch('backend.tasks._check_ansible_result')
    @mock.patch('backend.tasks.get_named_keys', return_value={'key-1': "ssh", 'key-2': "ssh2"})
    @mock.patch('backend.tasks.lambda_instance_manager')
    @mock.patch('backend.tasks.events.insert_cluster_info')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.events.create_new_lambda_instance')
    def test_create_lambda_instance_commons_fail(self, mock_create_new_lambda_instance_event,
                                                 mock_set_lambda_instance_status_event,
                                                 mock_insert_cluster_info_event,
                                                 mock_lambda_instance_manager_fokia,
                                                 mock_get_named_keys, mock_check_ansible_result,
                                                 mock_create_lambda_instance_central_vm,
                                                 mock_set_lambda_instance_status_central_vm):
        # Setup mock return values and side effects.
        mock_ansible_manager = mock.Mock()
        mock_provisioner_response = mock.Mock()

        mock_lambda_instance_manager_fokia.create_cluster.return_value = mock_ansible_manager,\
                                                                         mock_provisioner_response

        mock_ansible_result = mock.Mock()
        mock_lambda_instance_manager_fokia.run_playbook.return_value = mock_ansible_result

        mock_check_ansible_result.side_effect = ["Ansible successful", "Ansible task failed"]
        # Create the input that will be given to the task.
        specs = {
            'instance_name': "Lambda Instance created from Tests",
            'public_key_name': ['key-1', 'key-2'],
            'master_name': "master_name",
            'slaves': 2,
            'vcpus_master': 4,
            'vcpus_slave': 8,
            'ram_master': 4096,
            'ram_slave': 8192,
            'disk_master': 20,
            'disk_slave': 40,
            'ip_allocation': 'master',
            'network_request': 1,
            'project_name': "lambda.grnet.gr"
        }
        lambda_info = LambdaInfo(specs)

        # Call create lambda instance task.
        tasks.create_lambda_instance(lambda_info, self.AUTHENTICATION_TOKEN)

        # Assert that the proper mocks have been called.
        mock_create_new_lambda_instance_event.delay.\
            assert_called_with(instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_create_lambda_instance_central_vm.delay.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_get_named_keys.assert_called_with(self.AUTHENTICATION_TOKEN,
                                               names=['key-1', 'key-2'])
        mock_lambda_instance_manager_fokia.create_cluster.\
            assert_called_with(cluster_id=None,
                               auth_token=self.AUTHENTICATION_TOKEN, master_name="master_name",
                               slaves=2, vcpus_master=4, vcpus_slave=8, ram_master=4096,
                               ram_slave=8192, disk_master=20, disk_slave=40,
                               ip_allocation="master", network_request=1,
                               project_name="lambda.grnet.gr",
                               pub_keys={'key-1': "ssh", 'key-2': "ssh2"})
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.CLUSTER_CREATED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.CLUSTER_CREATED, "")
        mock_insert_cluster_info_event.delay.\
            assert_called_with(instance_uuid=None, provisioner_response=mock_provisioner_response,
                               specs=specs)

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'initialize.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.INIT_DONE)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.INIT_DONE, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'common-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.COMMONS_FAILED,
                            failure_message="Ansible task failed")
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.COMMONS_FAILED,
                            "Ansible task failed")

    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.central_vm_tasks.create_lambda_instance_central_vm')
    @mock.patch('backend.tasks._check_ansible_result')
    @mock.patch('backend.tasks.get_named_keys', return_value={'key-1': "ssh", 'key-2': "ssh2"})
    @mock.patch('backend.tasks.lambda_instance_manager')
    @mock.patch('backend.tasks.events.insert_cluster_info')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.events.create_new_lambda_instance')
    def test_create_lambda_instance_hadoop_fail(self, mock_create_new_lambda_instance_event,
                                                mock_set_lambda_instance_status_event,
                                                mock_insert_cluster_info_event,
                                                mock_lambda_instance_manager_fokia,
                                                mock_get_named_keys, mock_check_ansible_result,
                                                mock_create_lambda_instance_central_vm,
                                                mock_set_lambda_instance_status_central_vm):
        # Setup mock return values and side effects.
        mock_ansible_manager = mock.Mock()
        mock_provisioner_response = mock.Mock()

        mock_lambda_instance_manager_fokia.create_cluster.return_value = mock_ansible_manager,\
                                                                         mock_provisioner_response

        mock_ansible_result = mock.Mock()
        mock_lambda_instance_manager_fokia.run_playbook.return_value = mock_ansible_result

        mock_check_ansible_result.side_effect = ["Ansible successful",
                                                 "Ansible successful",
                                                 "Ansible task failed"]

        # Create the input that will be given to the task.
        specs = {
            'instance_name': "Lambda Instance created from Tests",
            'public_key_name': ['key-1', 'key-2'],
            'master_name': "master_name",
            'slaves': 2,
            'vcpus_master': 4,
            'vcpus_slave': 8,
            'ram_master': 4096,
            'ram_slave': 8192,
            'disk_master': 20,
            'disk_slave': 40,
            'ip_allocation': 'master',
            'network_request': 1,
            'project_name': "lambda.grnet.gr"
        }
        lambda_info = LambdaInfo(specs)

        # Call create lambda instance task.
        tasks.create_lambda_instance(lambda_info, self.AUTHENTICATION_TOKEN)

        # Assert that the proper mocks have been called.
        mock_create_new_lambda_instance_event.delay.\
            assert_called_with(instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_create_lambda_instance_central_vm.delay.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_get_named_keys.assert_called_with(self.AUTHENTICATION_TOKEN,
                                               names=['key-1', 'key-2'])
        mock_lambda_instance_manager_fokia.create_cluster.\
            assert_called_with(cluster_id=None,
                               auth_token=self.AUTHENTICATION_TOKEN, master_name="master_name",
                               slaves=2, vcpus_master=4, vcpus_slave=8, ram_master=4096,
                               ram_slave=8192, disk_master=20, disk_slave=40,
                               ip_allocation="master", network_request=1,
                               project_name="lambda.grnet.gr",
                               pub_keys={'key-1': "ssh", 'key-2': "ssh2"})
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.CLUSTER_CREATED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.CLUSTER_CREATED, "")
        mock_insert_cluster_info_event.delay.\
            assert_called_with(instance_uuid=None, provisioner_response=mock_provisioner_response,
                               specs=specs)

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'initialize.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.INIT_DONE)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.INIT_DONE, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'common-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.COMMONS_INSTALLED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.COMMONS_INSTALLED, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'hadoop-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.HADOOP_FAILED,
                            failure_message="Ansible task failed")
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.HADOOP_FAILED,
                            "Ansible task failed")

    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.central_vm_tasks.create_lambda_instance_central_vm')
    @mock.patch('backend.tasks._check_ansible_result')
    @mock.patch('backend.tasks.get_named_keys', return_value={'key-1': "ssh", 'key-2': "ssh2"})
    @mock.patch('backend.tasks.lambda_instance_manager')
    @mock.patch('backend.tasks.events.insert_cluster_info')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.events.create_new_lambda_instance')
    def test_create_lambda_instance_kafka_fail(self, mock_create_new_lambda_instance_event,
                                                mock_set_lambda_instance_status_event,
                                                mock_insert_cluster_info_event,
                                                mock_lambda_instance_manager_fokia,
                                                mock_get_named_keys, mock_check_ansible_result,
                                                mock_create_lambda_instance_central_vm,
                                                mock_set_lambda_instance_status_central_vm):
        # Setup mock return values and side effects.
        mock_ansible_manager = mock.Mock()
        mock_provisioner_response = mock.Mock()

        mock_lambda_instance_manager_fokia.create_cluster.return_value = mock_ansible_manager,\
                                                                         mock_provisioner_response

        mock_ansible_result = mock.Mock()
        mock_lambda_instance_manager_fokia.run_playbook.return_value = mock_ansible_result

        mock_check_ansible_result.side_effect = ["Ansible successful",
                                                 "Ansible successful",
                                                 "Ansible successful",
                                                 "Ansible task failed"]

        # Create the input that will be given to the task.
        specs = {
            'instance_name': "Lambda Instance created from Tests",
            'public_key_name': ['key-1', 'key-2'],
            'master_name': "master_name",
            'slaves': 2,
            'vcpus_master': 4,
            'vcpus_slave': 8,
            'ram_master': 4096,
            'ram_slave': 8192,
            'disk_master': 20,
            'disk_slave': 40,
            'ip_allocation': 'master',
            'network_request': 1,
            'project_name': "lambda.grnet.gr"
        }
        lambda_info = LambdaInfo(specs)

        # Call create lambda instance task.
        tasks.create_lambda_instance(lambda_info, self.AUTHENTICATION_TOKEN)

        # Assert that the proper mocks have been called.
        mock_create_new_lambda_instance_event.delay.\
            assert_called_with(instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_create_lambda_instance_central_vm.delay.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_get_named_keys.assert_called_with(self.AUTHENTICATION_TOKEN,
                                               names=['key-1', 'key-2'])
        mock_lambda_instance_manager_fokia.create_cluster.\
            assert_called_with(cluster_id=None,
                               auth_token=self.AUTHENTICATION_TOKEN, master_name="master_name",
                               slaves=2, vcpus_master=4, vcpus_slave=8, ram_master=4096,
                               ram_slave=8192, disk_master=20, disk_slave=40,
                               ip_allocation="master", network_request=1,
                               project_name="lambda.grnet.gr",
                               pub_keys={'key-1': "ssh", 'key-2': "ssh2"})
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.CLUSTER_CREATED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.CLUSTER_CREATED, "")
        mock_insert_cluster_info_event.delay.\
            assert_called_with(instance_uuid=None, provisioner_response=mock_provisioner_response,
                               specs=specs)

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'initialize.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.INIT_DONE)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.INIT_DONE, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'common-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.COMMONS_INSTALLED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.COMMONS_INSTALLED, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'hadoop-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.HADOOP_INSTALLED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.HADOOP_INSTALLED, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'kafka-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.KAFKA_FAILED,
                            failure_message="Ansible task failed")
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.KAFKA_FAILED,
                            "Ansible task failed")

    @mock.patch('backend.central_vm_tasks.set_lambda_instance_status_central_vm')
    @mock.patch('backend.central_vm_tasks.create_lambda_instance_central_vm')
    @mock.patch('backend.tasks._check_ansible_result')
    @mock.patch('backend.tasks.get_named_keys', return_value={'key-1': "ssh", 'key-2': "ssh2"})
    @mock.patch('backend.tasks.lambda_instance_manager')
    @mock.patch('backend.tasks.events.insert_cluster_info')
    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    @mock.patch('backend.tasks.events.create_new_lambda_instance')
    def test_create_lambda_instance_flink_fail(self, mock_create_new_lambda_instance_event,
                                               mock_set_lambda_instance_status_event,
                                               mock_insert_cluster_info_event,
                                               mock_lambda_instance_manager_fokia,
                                               mock_get_named_keys, mock_check_ansible_result,
                                               mock_create_lambda_instance_central_vm,
                                               mock_set_lambda_instance_status_central_vm):
        # Setup mock return values and side effects.
        mock_ansible_manager = mock.Mock()
        mock_provisioner_response = mock.Mock()

        mock_lambda_instance_manager_fokia.create_cluster.return_value = mock_ansible_manager,\
                                                                         mock_provisioner_response

        mock_ansible_result = mock.Mock()
        mock_lambda_instance_manager_fokia.run_playbook.return_value = mock_ansible_result

        mock_check_ansible_result.side_effect = ["Ansible successful",
                                                 "Ansible successful",
                                                 "Ansible successful",
                                                 "Ansible successful",
                                                 "Ansible task failed"]

        # Create the input that will be given to the task.
        specs = {
            'instance_name': "Lambda Instance created from Tests",
            'public_key_name': ['key-1', 'key-2'],
            'master_name': "master_name",
            'slaves': 2,
            'vcpus_master': 4,
            'vcpus_slave': 8,
            'ram_master': 4096,
            'ram_slave': 8192,
            'disk_master': 20,
            'disk_slave': 40,
            'ip_allocation': 'master',
            'network_request': 1,
            'project_name': "lambda.grnet.gr"
        }
        lambda_info = LambdaInfo(specs)

        # Call create lambda instance task.
        tasks.create_lambda_instance(lambda_info, self.AUTHENTICATION_TOKEN)

        # Assert that the proper mocks have been called.
        mock_create_new_lambda_instance_event.delay.\
            assert_called_with(instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_create_lambda_instance_central_vm.delay.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=None,
                               instance_name="Lambda Instance created from Tests",
                               specs=json.dumps(specs))
        mock_get_named_keys.assert_called_with(self.AUTHENTICATION_TOKEN,
                                               names=['key-1', 'key-2'])
        mock_lambda_instance_manager_fokia.create_cluster.\
            assert_called_with(cluster_id=None,
                               auth_token=self.AUTHENTICATION_TOKEN, master_name="master_name",
                               slaves=2, vcpus_master=4, vcpus_slave=8, ram_master=4096,
                               ram_slave=8192, disk_master=20, disk_slave=40,
                               ip_allocation="master", network_request=1,
                               project_name="lambda.grnet.gr",
                               pub_keys={'key-1': "ssh", 'key-2': "ssh2"})
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.CLUSTER_CREATED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.CLUSTER_CREATED, "")
        mock_insert_cluster_info_event.delay.\
            assert_called_with(instance_uuid=None, provisioner_response=mock_provisioner_response,
                               specs=specs)

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'initialize.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.INIT_DONE)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.INIT_DONE, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'common-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.COMMONS_INSTALLED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.COMMONS_INSTALLED, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'hadoop-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.HADOOP_INSTALLED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.HADOOP_INSTALLED, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'kafka-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.KAFKA_INSTALLED)
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.KAFKA_INSTALLED, "")

        mock_lambda_instance_manager_fokia.run_playbook.assert_any_call(mock_ansible_manager,
                                                                        'flink-install.yml')
        mock_check_ansible_result.assert_any_call(mock_ansible_result)
        mock_set_lambda_instance_status_event.delay.\
            assert_any_call(instance_uuid=None, status=LambdaInstance.FLINK_FAILED,
                            failure_message="Ansible task failed")
        mock_set_lambda_instance_status_central_vm.delay.\
            assert_any_call(self.AUTHENTICATION_TOKEN, None, LambdaInstance.FLINK_FAILED,
                            "Ansible task failed")


class TestHelperFunctions(APITestCase):
    """
    Contains tests for helper functions of Celery tasks.
    """

    def test_get_master_node_info(self):
        # Create a lambda instance on the database.
        lambda_instance_uuid = uuid.uuid4()
        lambda_instance = LambdaInstance.objects.create(uuid=lambda_instance_uuid)

        # Create a server on the database.
        master_node = Server.objects.create(id=10, lambda_instance=lambda_instance)
        lambda_instance.master_node = master_node
        lambda_instance.save()

        # Call get_master_node_info.
        response = tasks.get_master_node_info(lambda_instance_uuid)

        # Assert the response contents.
        self.assertEqual(response[0], 10)
        self.assertEqual(response[1], "snf-10.vm.okeanos.grnet.gr")

    def test_check_ansible_result(self):
        ansible_result = {
            'key-1': {
                'unreachable': "snf-10.vm.okeanos.grnet.gr"
            }
        }
        response = tasks._check_ansible_result(ansible_result)
        self.assertEqual(response, "Host unreachable")

        ansible_result = {
            'key-1': {
                'unreachable': 0,
                'failures': 10
            }
        }
        response = tasks._check_ansible_result(ansible_result)
        self.assertEqual(response, "Ansible task failed")

        ansible_result = {}
        response = tasks._check_ansible_result(ansible_result)
        self.assertEqual(response, "Ansible successful")

    @mock.patch('backend.tasks.events.set_lambda_instance_status')
    def test_on_failure(self, mock_set_lambda_instance_status_event):
        mock_exception = mock.Mock()
        mock_exception.message = "exception-message"

        task_id = uuid.uuid4()

        tasks.on_failure(mock_exception, task_id, None, None, None)

        mock_set_lambda_instance_status_event.delay.\
            assert_called_with(instance_uuid=task_id, status=LambdaInstance.FAILED,
                               failure_message="exception-message")
