from celery import shared_task

from .models import LambdaInstance, Server, PrivateNetwork, Application,\
    LambdaInstanceApplicationConnection


@shared_task
def create_new_lambda_instance(instance_uuid, instance_name, specs='{}'):
    """
    Creates a new lambda instance entry into the DataBase
    A unique uuid that identifies the lambda instance is created,
    after checking that it does not belong to another lambda instance.
    The instance info is inserted in json format, the instance name is
    specified as argument, and the status is set to 'PENDING' (default)
    instance_uuid: The uuid of the lambda instance
    instance_name: The name of the lambda instance
    specs: A json string containing the cluster specifications
    """

    LambdaInstance.objects.create(
        uuid=instance_uuid, name=instance_name, instance_info=specs, status=LambdaInstance.PENDING)


@shared_task
def set_lambda_instance_status(instance_uuid, status, failure_message=""):
    """
    Sets the status of a specified lambda instance to the specified value.
    The existence of the lambda instance should have been previously checked.
    instance_uuid: The uuid of the lambda instance.
    status: The integer that specifies the new status of the specified lambda instance.
            For more information see models.py.
    """

    lambda_instance = LambdaInstance.objects.get(uuid=instance_uuid)
    lambda_instance.status = status
    lambda_instance.failure_message = failure_message
    lambda_instance.save()


@shared_task
def insert_cluster_info(instance_uuid, specs, provisioner_response):
    """
    Inserts the information of the created cluster into the DataBase.
    instance_uuid: The uuid of the lambda instance
    specs: A dictionary containing the cluster specifications
    provisioner_response: The response of the cluster creator, containing ips, ids, etc.
    """

    lambda_instance = LambdaInstance.objects.get(uuid=instance_uuid)
    master = provisioner_response['nodes']['master']
    master_node = Server.objects.\
        create(id=master['id'],
               lambda_instance=lambda_instance,
               cpus=specs['vcpus_master'],
               ram=specs['ram_master'],
               disk=specs['disk_master'],
               priv_ip=master['internal_ip'],
               pub_ip=provisioner_response['ips'][0]['floating_ip_address'],
               pub_ip_id=provisioner_response['ips'][0]['id'])
    lambda_instance.master_node = master_node
    lambda_instance.save()

    for slave in provisioner_response['nodes']['slaves']:
        Server.objects.create(id=slave['id'],
                              lambda_instance=lambda_instance,
                              cpus=specs['vcpus_slave'],
                              ram=specs['ram_slave'],
                              disk=specs['disk_slave'],
                              priv_ip=slave['internal_ip'])

    PrivateNetwork.objects.create(id=provisioner_response['vpn']['id'],
                                  lambda_instance=lambda_instance,
                                  subnet=provisioner_response['subnet']['cidr'],
                                  gateway=provisioner_response['subnet']['gateway_ip'])


@shared_task
def create_new_application(uuid, name, path, description, app_type, owner,
                           execution_environment_name):
    """
    Creates a new entry of an application on the database.
    :param uuid: The uuid of the new application.
    :param name: The name of the new application.
    :param path: The path where the new application is stored on Pithos.
    :param description: The provided description of the new application.
    :param app_type: The type of the new application.
    :param owner: The owner of the new application.
    :param execution_environment_name: The name given to the Apache Flink execution environment.
    """

    if app_type == 'batch':
        app_type = Application.BATCH
    elif app_type == 'streaming':
        app_type = Application.STREAMING

    Application.objects.create(uuid=uuid, name=name, path=path, description=description,
                               owner=owner, type=app_type,
                               execution_environment_name=execution_environment_name)


@shared_task
def delete_application(uuid):
    """
    Deletes a specified application from the database. The existence of the application should
    have been previously checked.
    :param uuid: The uuid of the application to be deleted.
    """

    Application.objects.get(uuid=uuid).delete()


@shared_task
def set_application_status(application_uuid, status, failure_message=""):
    """
    Sets the status of a specified application to the specified value.
    The existence of the application should have been previously checked.
    :param application_uuid: The uuid of the specified application.
    :param status: The value for the status of the application.
    :param failure_message:
    """

    application = Application.objects.get(uuid=application_uuid)
    application.status = status
    application.failure_message = failure_message
    application.save()


@shared_task
def create_lambda_instance_application_connection(lambda_instance_uuid, application_uuid):
    """
    Creates a new entry of a connection between a lambda instance and an application on the
    database. The existence of the lambda instance and the application should have been
    previously checked.
    :param lambda_instance_uuid: The uuid of the lambda instance.
    :param application_uuid: The uuid of the application
    """

    lambda_instance = LambdaInstance.objects.get(uuid=lambda_instance_uuid)
    application = Application.objects.get(uuid=application_uuid)
    LambdaInstanceApplicationConnection.objects.create(lambda_instance=lambda_instance,
                                                       application=application)


@shared_task
def delete_lambda_instance_application_connection(lambda_instance_uuid, application_uuid):
    """
    Deletes an entry of a connection between a lambda instance an an application on the database.
    The existence of the lambda instance and the application should have been previously checked.
    :param lambda_instance_uuid: The uuid of the lambda instance.
    :param application_uuid: The uuid of the application.
    """

    lambda_instance = LambdaInstance.objects.get(uuid=lambda_instance_uuid)
    application = Application.objects.get(uuid=application_uuid)
    LambdaInstanceApplicationConnection.objects.get(lambda_instance=lambda_instance,
                                                    application=application).delete()


@shared_task
def start_stop_application(lambda_instance_uuid, application_uuid, action, app_type):
    lambda_instance = LambdaInstance.objects.get(uuid=lambda_instance_uuid)
    application = Application.objects.get(uuid=application_uuid)
    instanceapplication = LambdaInstanceApplicationConnection.objects.\
        get(lambda_instance=lambda_instance, application=application)
    if action == 'start':
        instanceapplication.started = True
        if app_type == 'batch':
            lambda_instance.started_batch = True
        else:
            lambda_instance.started_streaming = True
    else:
        instanceapplication.started = False
        if app_type == 'batch':
            lambda_instance.started_batch = False
        else:
            lambda_instance.started_streaming = False
    instanceapplication.save()
    lambda_instance.save()
