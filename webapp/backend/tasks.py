import json
from celery import shared_task

from kamaki.clients import ClientError

from fokia import utils

from .models import LambdaInstance
from fokia import lambda_instance_manager
from . import events


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
def create_lambda_instance(auth_token=None, instance_name='Lambda Instance',
                           master_name='lambda-master',
                           slaves=1, vcpus_master=4, vcpus_slave=4,
                           ram_master=4096, ram_slave=4096,
                           disk_master=40, disk_slave=40, ip_allocation='master',
                           network_request=1, project_name='lambda.grnet.gr'):
    specs_dict = {'master_name': master_name, 'slaves': slaves,
                  'vcpus_master': vcpus_master, 'vcpus_slave': vcpus_slave,
                  'ram_master': ram_master, 'ram_slave': ram_slave,
                  'disk_master': disk_master, 'disk_slave': disk_slave,
                  'ip_allocation': ip_allocation, 'network_request': network_request,
                  'project_name': project_name}
    specs = json.dumps(specs_dict)

    instance_uuid = create_lambda_instance.request.id
    events.create_new_lambda_instance.delay(instance_uuid=instance_uuid,
                                            instance_name=instance_name, specs=specs)

    try:
        ansible_manager, provisioner_response = \
            lambda_instance_manager.create_cluster(cluster_id=instance_uuid,
                                                   auth_token=auth_token,
                                                   master_name=master_name,
                                                   slaves=slaves,
                                                   vcpus_master=vcpus_master,
                                                   vcpus_slave=vcpus_slave,
                                                   ram_master=ram_master,
                                                   ram_slave=ram_slave,
                                                   disk_master=disk_master,
                                                   disk_slave=disk_slave,
                                                   ip_allocation=ip_allocation,
                                                   network_request=network_request,
                                                   project_name=project_name)
    except ClientError as exception:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.CLUSTER_FAILED,
                                                failure_message=exception.message)
        return

    events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                            status=LambdaInstance.CLUSTER_CREATED)

    events.insert_cluster_info.delay(instance_uuid=instance_uuid,
                                     specs=specs_dict,
                                     provisioner_response=provisioner_response)

    ansible_result = lambda_instance_manager.run_playbook(ansible_manager, 'initialize.yml')
    check = check_ansible_result(ansible_result)
    if check != 'Ansible successful':
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.INIT_FAILED,
                                                failure_message=check)
        return
    else:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.INIT_DONE)

    ansible_result = lambda_instance_manager.run_playbook(ansible_manager, 'common-install.yml')
    check = check_ansible_result(ansible_result)
    if check != 'Ansible successful':
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.COMMONS_FAILED,
                                                failure_message=check)
        return
    else:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.COMMONS_INSTALLED)

    ansible_result = lambda_instance_manager.run_playbook(ansible_manager, 'hadoop-install.yml')
    check = check_ansible_result(ansible_result)
    if check != 'Ansible successful':
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.HADOOP_FAILED,
                                                failure_message=check)
        return
    else:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.HADOOP_INSTALLED)

    ansible_result = lambda_instance_manager.run_playbook(ansible_manager, 'kafka-install.yml')
    check = check_ansible_result(ansible_result)
    if check != 'Ansible successful':
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.KAFKA_FAILED,
                                                failure_message=check)
        return
    else:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.KAFKA_INSTALLED)

    ansible_result = lambda_instance_manager.run_playbook(ansible_manager, 'flink-install.yml')
    check = check_ansible_result(ansible_result)
    if check != 'Ansible successful':
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.FLINK_FAILED,
                                                failure_message=check)
        return
    else:
        events.set_lambda_instance_status.delay(instance_uuid=instance_uuid,
                                                status=LambdaInstance.FLINK_INSTALLED)


def on_failure(exc, task_id, args, kwargs, einfo):
    events.set_lambda_instance_status.delay(instance_uuid=task_id,
                                            status=LambdaInstance.FAILED,
                                            failure_message=exc.message)


setattr(create_lambda_instance, 'on_failure', on_failure)


def check_ansible_result(ansible_result):
    for _, value in ansible_result.iteritems():
        if value['unreachable'] != 0:
            return 'Host unreachable'
        if value['failures'] != 0:
            return 'Ansible task failed'
    return 'Ansible successful'
