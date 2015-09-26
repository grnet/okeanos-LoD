import json

from os import path, mkdir, remove, system

from celery import shared_task
from django.conf import settings

from rest_framework import status

from kamaki.clients import ClientError
from fokia import utils
from fokia import lambda_instance_manager
from fokia.ansible_manager import Manager
from . import events
from .models import LambdaInstance, Application
from .authenticate_user import get_named_keys

@shared_task
def lambda_instance_start(instance_uuid, auth_url, auth_token, master_id, slave_ids):
    """
    Starts the VMs of a lambda instance using kamaki. Starting the master node will cause the lambda
    services to start. That is why all slave nodes must be started before starting the master node.
    :param instance_uuid: The uuid of the lambda instance.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the owner of the lambda instance.
    :param master_id: The ~okeanos id of the VM that acts as the master node.
    :param slave_ids: The ~okeanos ids of the VMs that act as the slave nodes.
    """

    try:
        # Start the VMs of the specified lambda instance.
        utils.lambda_instance_start(auth_url, auth_token, master_id, slave_ids)

        # Update lambda instance status on the database to started.
        events.set_lambda_instance_status.delay(instance_uuid, LambdaInstance.STARTED)
    except ClientError as exception:
        events.set_lambda_instance_status.delay(instance_uuid, LambdaInstance.FAILED,
                                                exception.message)


@shared_task
def lambda_instance_stop(instance_uuid, auth_url, auth_token, master_id, slave_ids):
    """
    Stops the VMs of a lambda instance using kamaki. Stopping the master node will cause the lambda
    services to stop. That is why the master node must be stopped before stopping any of the slave
    nodes.
    :param instance_uuid: The uuid of the lambda instance.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the owner of the lambda instance.
    :param master_id: The ~okeanos id of the VM that acts as the master node.
    :param slave_ids: The ~okeanos ids of the VMs that act as the slave nodes.
    """

    try:
        # Stop the VMs of the specified lambda instance.
        utils.lambda_instance_stop(auth_url, auth_token, master_id, slave_ids)

        # Update lambda instance status on the database to started.
        events.set_lambda_instance_status.delay(instance_uuid, LambdaInstance.STOPPED)
    except ClientError as exception:
        events.set_lambda_instance_status.delay(instance_uuid, LambdaInstance.FAILED,
                                                exception.message)


@shared_task
def lambda_instance_destroy(instance_uuid, auth_url, auth_token, master_id, slave_ids,
                            public_ip_id, private_network_id):
    """
    Destroys the specified lambda instance. The VMs of the lambda instance, along with the public
    ip and the private network used are destroyed and the status of the lambda instance gets
    changed to DESTROYED. There is no going back from this state, the entries are kept to the
    database for reference.
    :param instance_uuid: The uuid of the lambda instance.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the owner of the lambda instance.
    :param master_id: The ~okeanos id of the VM that acts as the master node.
    :param slave_ids: The ~okeanos ids of the VMs that act as the slave nodes.
    :param public_ip_id: The ~okeanos id of the public ip assigned to master node.
    :param private_network_id: The ~okeanos id of the private network used by the lambda instance.
    """

    try:
        # Destroy all VMs, the public ip and the private network of the lambda instance.
        lambda_instance_manager.lambda_instance_destroy(
            instance_uuid,
            auth_url,
            auth_token,
            master_id,
            slave_ids,
            public_ip_id,
            private_network_id)

        # Update lambda instance status on the database to destroyed.
        events.set_lambda_instance_status.delay(instance_uuid, LambdaInstance.DESTROYED)
    except ClientError as exception:
        events.set_lambda_instance_status.delay(instance_uuid, LambdaInstance.FAILED,
                                                exception.message)


@shared_task
def create_lambda_instance(lambda_info, auth_token):
    specs = lambda_info.data
    specs_json = json.dumps(specs)
    instance_uuid = create_lambda_instance.request.id
    events.create_new_lambda_instance.delay(instance_uuid=instance_uuid,
                                            instance_name=specs['instance_name'],
                                            specs=specs_json)

    pub_keys = []
    if specs.get('public_key_name'):
        pub_keys = get_named_keys(auth_token, names=specs['public_key_name'])

    try:
        ansible_manager, provisioner_response = \
            lambda_instance_manager.create_cluster(cluster_id=instance_uuid,
                                                   auth_token=auth_token,
                                                   master_name=specs['master_name'],
                                                   slaves=specs['slaves'],
                                                   vcpus_master=specs['vcpus_master'],
                                                   vcpus_slave=specs['vcpus_slave'],
                                                   ram_master=specs['ram_master'],
                                                   ram_slave=specs['ram_slave'],
                                                   disk_master=specs['disk_master'],
                                                   disk_slave=specs['disk_slave'],
                                                   ip_allocation=specs['ip_allocation'],
                                                   network_request=specs['network_request'],
                                                   project_name=specs['project_name'],
                                                   pub_keys=pub_keys)
    except ClientError as exception:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.CLUSTER_FAILED,
                                                failure_message=exception.message)
        return

    events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                            status=LambdaInstance.CLUSTER_CREATED)

    events.insert_cluster_info.delay(instance_uuid=instance_uuid,
                                     specs=lambda_info.data,
                                     provisioner_response=provisioner_response)

    ansible_result = lambda_instance_manager.run_playbook(ansible_manager, 'initialize.yml')
    check = __check_ansible_result(ansible_result)
    if check != 'Ansible successful':
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.INIT_FAILED,
                                                failure_message=check)
        return
    else:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.INIT_DONE)

    ansible_result = lambda_instance_manager.run_playbook(ansible_manager, 'common-install.yml')
    check = __check_ansible_result(ansible_result)
    if check != 'Ansible successful':
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.COMMONS_FAILED,
                                                failure_message=check)
        return
    else:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.COMMONS_INSTALLED)

    ansible_result = lambda_instance_manager.run_playbook(ansible_manager, 'hadoop-install.yml')
    check = __check_ansible_result(ansible_result)
    if check != 'Ansible successful':
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.HADOOP_FAILED,
                                                failure_message=check)
        return
    else:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.HADOOP_INSTALLED)

    ansible_result = lambda_instance_manager.run_playbook(ansible_manager, 'kafka-install.yml')
    check = __check_ansible_result(ansible_result)
    if check != 'Ansible successful':
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.KAFKA_FAILED,
                                                failure_message=check)
        return
    else:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.KAFKA_INSTALLED)

    ansible_result = lambda_instance_manager.run_playbook(ansible_manager, 'flink-install.yml')
    check = __check_ansible_result(ansible_result)
    if check != 'Ansible successful':
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.FLINK_FAILED,
                                                failure_message=check)
        return
    else:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.FLINK_INSTALLED)

    # Set lambda instance status to started.
    events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                            status=LambdaInstance.STARTED)


def __check_ansible_result(ansible_result):
    for _, value in ansible_result.iteritems():
        if value['unreachable'] != 0:
            return 'Host unreachable'
        if value['failures'] != 0:
            return 'Ansible task failed'
    return 'Ansible successful'


def on_failure(exc, task_id, args, kwargs, einfo):
    events.set_lambda_instance_status.delay(instance_uuid=task_id,
                                            status=LambdaInstance.FAILED,
                                            failure_message=exc.message)


setattr(create_lambda_instance, 'on_failure', on_failure)


@shared_task
def upload_application_to_pithos(auth_url, auth_token, container_name, project_name,
                                 local_file_path, application_uuid):
    """
    Uploads an application to Pithos.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the user.
    :param container_name: The name of the Pithos container where the file will be uploaded.
    :param local_file_path: The path on the local file system of the file to be uploaded.
    :param application_uuid: The uuid of the application to be uploaded.
    """

    # Open file from the local file system.
    local_file = open(local_file_path, 'r')

    try:
        utils.upload_file_to_pithos(auth_url, auth_token, container_name, project_name, local_file)

        events.set_application_status.delay(application_uuid=application_uuid,
                                            status=Application.UPLOADED)
    except ClientError as exception:
        events.set_application_status.delay(application_uuid, Application.FAILED,
                                            exception.message)

    # Release local file system resources.
    local_file.close()

    # Remove the file saved on the local file system.
    remove(local_file_path)


@shared_task
def delete_application_from_pithos(auth_url, auth_token, container_name, filename,
                                   application_uuid):
    """
    Deletes an application from Pithos.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the user.
    :param container_name: The name of the Pithos container where the file will be uploaded.
    :param filename: The name of the application to be deleted.
    :param application_uuid: The uuid of the application to be deleted.
    """

    try:
        utils.delete_file_from_pithos(auth_url, auth_token, container_name, filename)

        events.delete_application.delay(application_uuid)
    except ClientError as exception:
        # If the file is not found on Pithos, the entry on the database should be still
        # deleted.
        if exception.status == status.HTTP_404_NOT_FOUND:
            events.delete_application.delay(application_uuid)
        else:
            events.set_application_status.delay(application_uuid, Application.FAILED,
                                                exception.message)


@shared_task
def deploy_application(auth_url, auth_token, container_name, lambda_instance_uuid,
                       application_uuid):
    """
    Deployes an application from Pithos to a specified lambda instance.
    :param auth_url: The authentication url for ~okeanos API.
    :param auth_token: The authentication token of the user.
    :param container_name: The name of the Pithos container where the file will be uploaded.
    :param lambda_instance_uuid: The uuid of the lambda instance.
    :param application_uuid: The uuid of the applcation.
    """

    # Get the name of the application.
    application_name = Application.objects.get(uuid=application_uuid).name

    # Dowload application from Pithos.
    if not path.exists(settings.TEMPORARY_FILE_STORAGE):
        mkdir(settings.TEMPORARY_FILE_STORAGE)
    local_file_path = path.join(settings.TEMPORARY_FILE_STORAGE, application_name)
    local_file = open(local_file_path, 'w+')

    try:
        utils.download_file_from_pithos(auth_url, auth_token, container_name, application_name,
                                        local_file)
    except ClientError as exception:
        events.set_application_status.delay(application_uuid, Application.FAILED,
                                            exception.message)
    local_file.close()

    # Get the hostname of the master node of the specified lambda instance.
    master_node_hostname = get_master_node_info(lambda_instance_uuid)[1]

    # Move the application on the specified master node using scp.
    system("scp {path} root@{hostname}:/home/flink/".format(path=local_file_path,
                                                            hostname=master_node_hostname))

    # Delete the application from the local file system.
    remove(local_file_path)

    # Create a new entry on the database.
    events.create_lambda_instance_application_connection.delay(lambda_instance_uuid,
                                                               application_uuid)


@shared_task
def withdraw_application(lambda_instance_uuid, application_uuid):
    """
    Withdraws an application from a specified lambda instance.
    :param lambda_instance_uuid: The uuid of the lambda instance.
    :param application_uuid: The uuid of the application.
    """

    # Get the name of the application.
    application_name = Application.objects.get(uuid=application_uuid).name

    # Get the hostname of the master node of the specified lambda instance.
    master_node_hostname = get_master_node_info(lambda_instance_uuid)[1]

    # Delete the application from the master node.
    system("ssh -l root {hostname} rm /home/flink/{filename}".format(hostname=master_node_hostname,
                                                                     filename=application_name))

    # Create an event to remove the connection between the lambda instance and the application
    # on the database.
    events.delete_lambda_instance_application_connection.delay(lambda_instance_uuid,
                                                               application_uuid)


@shared_task
def start_stop_application(lambda_instance_uuid, app_uuid,
                           app_action, app_type, jar_filename=None):
    master_node_id = get_master_node_info(lambda_instance_uuid)[0]
    response = {'nodes': {'master': {'id': master_node_id, 'internal_ip': None}}}
    ansible_manager = Manager(response)
    ansible_manager.create_master_inventory(app_action=app_action, app_type=app_type,
                                            jar_filename=jar_filename)
    ansible_result = lambda_instance_manager.run_playbook(ansible_manager, 'flink-apps.yml')
    check = __check_ansible_result(ansible_result)
    if check == 'Ansible successful':
        events.start_stop_application(lambda_instance_uuid=lambda_instance_uuid,
                                      application_uuid=app_uuid,
                                      action=app_action, app_type=app_type)


def get_master_node_info(lambda_instance_uuid):
    """
    Returns the id and the full hostname of the master node of a specified lambda instance.
    :param lambda_instance_uuid: The uuid of the lambda instance.
    :return: The id and the full hostname of the master node of the specified lambda instance.
    """

    master_node_id = LambdaInstance.objects.get(uuid=lambda_instance_uuid).master_node.id

    master_node_hostname = "snf-{master_node_id}.vm.okeanos.grnet.gr". \
        format(master_node_id=master_node_id)

    return master_node_id, master_node_hostname
