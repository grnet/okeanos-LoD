import mock
import uuid

from rest_framework.test import APITestCase

from backend import central_vm_tasks
from backend.models import LambdaInstance, Application


class CustomTimeoutException(Exception):
    """
    Class that emulates requests Timeout exception.
    """

    def __init__(self):
        super(CustomTimeoutException, self).__init__()


class CustomConnectionError(Exception):
    """
    Class that emulates requests ConnectionError exception.
    """

    def __init__(self):
        super(CustomConnectionError, self).__init__()


class TestCeleryCentralVMTasks(APITestCase):
    """
    Contains tests for Central VM Celery tasks.
    """

    # Define a fake ~okeanos token.
    AUTHENTICATION_TOKEN = "fake-token"

    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_create_lambda_instance_central_vm(self, mock_requests, mock_settings):
        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"

        # Create the parameters that will be given as input to the task.
        instance_uuid = uuid.uuid4()
        instance_name = "instance_name"
        specs = "specs"

        # Call the task.
        central_vm_tasks.create_lambda_instance_central_vm(self.AUTHENTICATION_TOKEN,
                                                           instance_uuid, instance_name, specs)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_instances/",
            json={
                'uuid': instance_uuid,
                'name': instance_name,
                'instance_info': specs,
                'status': LambdaInstance.PENDING,
                'failure_message': ""
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

    @mock.patch('backend.central_vm_tasks.requests.exceptions.Timeout', new=CustomTimeoutException)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_create_lambda_instance_central_vm_timeout_except(self, mock_requests, mock_settings):
        # Set side effects for mocks.
        mock_requests.post.side_effect = CustomTimeoutException()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        instance_uuid = uuid.uuid4()
        instance_name = "instance_name"
        specs = "specs"

        # Mock retry method of the task to be called.
        central_vm_tasks.create_lambda_instance_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.create_lambda_instance_central_vm(self.AUTHENTICATION_TOKEN,
                                                           instance_uuid, instance_name, specs)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_instances/",
            json={
                'uuid': instance_uuid,
                'name': instance_name,
                'instance_info': specs,
                'status': LambdaInstance.PENDING,
                'failure_message': ""
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )
        central_vm_tasks.create_lambda_instance_central_vm.retry.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=instance_uuid,
                               instance_name=instance_name, specs=specs,
                               countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)

    @mock.patch('backend.central_vm_tasks.requests.exceptions.ConnectionError',
                new=CustomConnectionError)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_create_lambda_instance_central_vm_connection_error_except(self, mock_requests,
                                                                       mock_settings):
        # Set side effects for mocks.
        mock_requests.post.side_effect = CustomConnectionError()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        instance_uuid = uuid.uuid4()
        instance_name = "instance_name"
        specs = "specs"

        # Mock retry method of the task to be called.
        central_vm_tasks.create_lambda_instance_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.create_lambda_instance_central_vm(self.AUTHENTICATION_TOKEN,
                                                           instance_uuid, instance_name, specs)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_instances/",
            json={
                'uuid': instance_uuid,
                'name': instance_name,
                'instance_info': specs,
                'status': LambdaInstance.PENDING,
                'failure_message': ""
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

        central_vm_tasks.create_lambda_instance_central_vm.retry.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=instance_uuid,
                               instance_name=instance_name, specs=specs,
                               countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)

    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_set_lambda_instance_status_central_vm(self, mock_requests, mock_settings):
        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"

        # Create the parameters that will be given as input to the task.
        instance_uuid = uuid.uuid4()
        status = "status"
        failure_message = "failure_message"

        # Call the task.
        central_vm_tasks.set_lambda_instance_status_central_vm(self.AUTHENTICATION_TOKEN,
                                                               instance_uuid, status,
                                                               failure_message)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_instances/{}".format(instance_uuid),
            json={
                'status': status,
                'failure_message': failure_message
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

    @mock.patch('backend.central_vm_tasks.requests.exceptions.Timeout', new=CustomTimeoutException)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_set_lambda_instance_status_central_vm_timeout_except(self, mock_requests,
                                                                  mock_settings):
        # Set side effects for mocks.
        mock_requests.post.side_effect = CustomTimeoutException()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        instance_uuid = uuid.uuid4()
        status = "status"
        failure_message = "failure_message"

        # Mock retry method of the task to be called.
        central_vm_tasks.set_lambda_instance_status_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.set_lambda_instance_status_central_vm(self.AUTHENTICATION_TOKEN,
                                                               instance_uuid, status,
                                                               failure_message)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_instances/{}".format(instance_uuid),
            json={
                'status': status,
                'failure_message': failure_message
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

        central_vm_tasks.set_lambda_instance_status_central_vm.retry\
            .assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                                instance_uuid=instance_uuid, status=status,
                                failure_message=failure_message,
                                countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)

    @mock.patch('backend.central_vm_tasks.requests.exceptions.ConnectionError',
                new=CustomConnectionError)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_set_lambda_instance_status_central_vm_connection_error_except(self, mock_requests,
                                                                           mock_settings):
        # Set side effects for mocks.
        mock_requests.post.side_effect = CustomConnectionError()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        instance_uuid = uuid.uuid4()
        status = "status"
        failure_message = "failure_message"

        # Mock retry method of the task to be called.
        central_vm_tasks.set_lambda_instance_status_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.set_lambda_instance_status_central_vm(self.AUTHENTICATION_TOKEN,
                                                               instance_uuid, status,
                                                               failure_message)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_instances/{}".format(instance_uuid),
            json={
                'status': status,
                'failure_message': failure_message
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

        central_vm_tasks.set_lambda_instance_status_central_vm.retry\
            .assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                                instance_uuid=instance_uuid, status=status,
                                failure_message=failure_message,
                                countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)

    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_delete_lambda_instance_central_vm(self, mock_requests, mock_settings):
        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"

        # Create the parameters that will be given as input to the task.
        instance_uuid = uuid.uuid4()

        # Call the task.
        central_vm_tasks.delete_lambda_instance_central_vm(self.AUTHENTICATION_TOKEN,
                                                           instance_uuid)

        # Assert that the proper mock calls have been made.
        mock_requests.delete.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_instances/{}".format(instance_uuid),
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

    @mock.patch('backend.central_vm_tasks.requests.exceptions.Timeout', new=CustomTimeoutException)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_delete_lambda_instance_central_vm_timeout_except(self, mock_requests,
                                                              mock_settings):
        # Set side effects for mocks.
        mock_requests.delete.side_effect = CustomTimeoutException()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        instance_uuid = uuid.uuid4()

        # Mock retry method of the task to be called.
        central_vm_tasks.delete_lambda_instance_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.delete_lambda_instance_central_vm(self.AUTHENTICATION_TOKEN,
                                                           instance_uuid)

        # Assert that the proper mock calls have been made.
        mock_requests.delete.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_instances/{}".format(instance_uuid),
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

        central_vm_tasks.delete_lambda_instance_central_vm.retry.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=instance_uuid,
                               countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)

    @mock.patch('backend.central_vm_tasks.requests.exceptions.ConnectionError',
                new=CustomConnectionError)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_delete_lambda_instance_central_vm_connection_error_except(self, mock_requests,
                                                                       mock_settings):
        # Set side effects for mocks.
        mock_requests.delete.side_effect = CustomConnectionError()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        instance_uuid = uuid.uuid4()

        # Mock retry method of the task to be called.
        central_vm_tasks.delete_lambda_instance_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.delete_lambda_instance_central_vm(self.AUTHENTICATION_TOKEN,
                                                           instance_uuid)

        # Assert that the proper mock calls have been made.
        mock_requests.delete.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_instances/{}".format(instance_uuid),
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

        central_vm_tasks.delete_lambda_instance_central_vm.retry.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=instance_uuid,
                               countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)

    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_create_application_central_vm(self, mock_requests, mock_settings):
        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"

        # Create the parameters that will be given as input to the task.
        application_uuid = uuid.uuid4()
        application_name = "instance_name"
        description = "description"

        # Call the task.
        central_vm_tasks.create_application_central_vm(self.AUTHENTICATION_TOKEN,
                                                       application_uuid, application_name,
                                                       description)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_applications/",
            json={
                'uuid': application_uuid,
                'name': application_name,
                'description': description,
                'status': Application.UPLOADING,
                'failure_message': ""
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

    @mock.patch('backend.central_vm_tasks.requests.exceptions.Timeout', new=CustomTimeoutException)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_create_application_central_vm_timeout_except(self, mock_requests, mock_settings):
        # Set side effects for mocks.
        mock_requests.post.side_effect = CustomTimeoutException()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        application_uuid = uuid.uuid4()
        application_name = "instance_name"
        description = "description"

        # Mock retry method of the task to be called.
        central_vm_tasks.create_application_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.create_application_central_vm(self.AUTHENTICATION_TOKEN,
                                                       application_uuid, application_name,
                                                       description)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_applications/",
            json={
                'uuid': application_uuid,
                'name': application_name,
                'description': description,
                'status': Application.UPLOADING,
                'failure_message': ""
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

        central_vm_tasks.create_application_central_vm.retry.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               application_uuid=application_uuid,
                               name=application_name, description=description,
                               countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)

    @mock.patch('backend.central_vm_tasks.requests.exceptions.ConnectionError',
                new=CustomConnectionError)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_create_application_central_vm_connection_error_except(self, mock_requests,
                                                                   mock_settings):
        # Set side effects for mocks.
        mock_requests.post.side_effect = CustomConnectionError()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        application_uuid = uuid.uuid4()
        application_name = "instance_name"
        description = "description"

        # Mock retry method of the task to be called.
        central_vm_tasks.create_application_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.create_application_central_vm(self.AUTHENTICATION_TOKEN,
                                                       application_uuid, application_name,
                                                       description)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_applications/",
            json={
                'uuid': application_uuid,
                'name': application_name,
                'description': description,
                'status': Application.UPLOADING,
                'failure_message': ""
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

        central_vm_tasks.create_application_central_vm.retry.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               application_uuid=application_uuid,
                               name=application_name, description=description,
                               countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)

    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_set_application_status_central_vm(self, mock_requests, mock_settings):
        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"

        # Create the parameters that will be given as input to the task.
        application_uuid = uuid.uuid4()
        status = "status"
        failure_message = "failure_message"

        # Call the task.
        central_vm_tasks.set_application_status_central_vm(self.AUTHENTICATION_TOKEN,
                                                           application_uuid, status,
                                                           failure_message)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_applications/{}".format(application_uuid),
            json={
                'status': status,
                'failure_message': "failure_message"
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

    @mock.patch('backend.central_vm_tasks.requests.exceptions.Timeout', new=CustomTimeoutException)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_set_application_status_central_vm_timeout_except(self, mock_requests,
                                                              mock_settings):
        # Set side effects for mocks.
        mock_requests.post.side_effect = CustomTimeoutException()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        application_uuid = uuid.uuid4()
        status = "status"
        failure_message = "failure_message"

        # Mock retry method of the task to be called.
        central_vm_tasks.set_application_status_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.set_application_status_central_vm(self.AUTHENTICATION_TOKEN,
                                                           application_uuid, status,
                                                           failure_message)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_applications/{}".format(application_uuid),
            json={
                'status': status,
                'failure_message': "failure_message"
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

        central_vm_tasks.set_application_status_central_vm.retry.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               application_uuid=application_uuid, status=status,
                               failure_message=failure_message,
                               countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)

    @mock.patch('backend.central_vm_tasks.requests.exceptions.ConnectionError',
                new=CustomConnectionError)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_set_application_status_central_vm_connection_error_except(self, mock_requests,
                                                                       mock_settings):
        # Set side effects for mocks.
        mock_requests.post.side_effect = CustomConnectionError()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        application_uuid = uuid.uuid4()
        status = "status"
        failure_message = "failure_message"

        # Mock retry method of the task to be called.
        central_vm_tasks.set_application_status_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.set_application_status_central_vm(self.AUTHENTICATION_TOKEN,
                                                           application_uuid, status,
                                                           failure_message)

        # Assert that the proper mock calls have been made.
        mock_requests.post.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_applications/{}".format(application_uuid),
            json={
                'status': status,
                'failure_message': "failure_message"
            },
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

        central_vm_tasks.set_application_status_central_vm.retry.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               application_uuid=application_uuid, status=status,
                               failure_message=failure_message,
                               countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)

    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_delete_application_central_vm(self, mock_requests, mock_settings):
        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"

        # Create the parameters that will be given as input to the task.
        application_uuid = uuid.uuid4()

        # Call the task.
        central_vm_tasks.delete_application_central_vm(self.AUTHENTICATION_TOKEN,
                                                       application_uuid)

        # Assert that the proper mock calls have been made.
        mock_requests.delete.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_applications/{}".format(application_uuid),
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

    @mock.patch('backend.central_vm_tasks.requests.exceptions.Timeout', new=CustomTimeoutException)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_delete_application_central_vm_timeout_except(self, mock_requests, mock_settings):
        # Set side effects for mocks.
        mock_requests.delete.side_effect = CustomTimeoutException()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        instance_uuid = uuid.uuid4()

        # Mock retry method of the task to be called.
        central_vm_tasks.delete_lambda_instance_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.delete_lambda_instance_central_vm(self.AUTHENTICATION_TOKEN,
                                                           instance_uuid)

        # Assert that the proper mock calls have been made.
        mock_requests.delete.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_instances/{}".format(instance_uuid),
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

        central_vm_tasks.delete_lambda_instance_central_vm.retry.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               instance_uuid=instance_uuid,
                               countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)

    @mock.patch('backend.central_vm_tasks.requests.exceptions.ConnectionError',
                new=CustomConnectionError)
    @mock.patch('backend.central_vm_tasks.settings')
    @mock.patch('backend.central_vm_tasks.requests')
    def test_delete_application_central_vm_connection_error_except(self, mock_requests,
                                                                   mock_settings):
        # Set side effects for mocks.
        mock_requests.delete.side_effect = CustomConnectionError()

        # Set the required values for the mocks.
        mock_settings.CENTRAL_VM_IP = "CENTRAL_VM_IP"
        mock_settings.CENTRAL_VM_RETRY_COUNTDOWN = "CENTRAL_VM_RETRY_COUNTDOWN"

        # Create the parameters that will be given as input to the task.
        application_uuid = uuid.uuid4()

        # Mock retry method of the task to be called.
        central_vm_tasks.delete_application_central_vm.retry = mock.Mock()

        # Call the task.
        central_vm_tasks.delete_application_central_vm(self.AUTHENTICATION_TOKEN,
                                                           application_uuid)

        # Assert that the proper mock calls have been made.
        mock_requests.delete.assert_called_with(
            url="http://CENTRAL_VM_IP/api/lambda_applications/{}".format(application_uuid),
            headers={
                'Authorization': "Token {}".format(self.AUTHENTICATION_TOKEN),
                'Content-Type': "application/json"
            }
        )

        central_vm_tasks.delete_application_central_vm.retry.\
            assert_called_with(auth_token=self.AUTHENTICATION_TOKEN,
                               application_uuid=application_uuid,
                               countdown=mock_settings.CENTRAL_VM_RETRY_COUNTDOWN)
