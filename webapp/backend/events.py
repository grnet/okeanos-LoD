from celery import shared_task

from .models import LambdaInstance
from .models import Server
from .models import PrivateNetwork


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
    Sets the status of a specified lambda instance to the specified status.
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
    Server.objects.create(id=master['id'],
                          lambda_instance=lambda_instance,
                          cpus=specs['vcpus_master'],
                          ram=specs['ram_master'],
                          disk=specs['disk_master'],
                          priv_ip=master['internal_ip'],
                          pub_ip=provisioner_response['ips']['floating_ip_address'],
                          pub_ip_id=provisioner_response['ips']['id'])

    for _, value in provisioner_response['nodes']['slaves'].iteritems():
        Server.objects.create(id=value['id'],
                              lambda_instance=lambda_instance,
                              cpus=specs['vcpus_slave'],
                              ram=specs['ram_slave'],
                              disk=specs['disk_slave'],
                              priv_ip=value['internal_ip'])

    PrivateNetwork.objects.create(id=provisioner_response['vpn']['id'],
                                  lambda_instance=lambda_instance,
                                  subnet=provisioner_response['subnet']['cidr'],
                                  gateway=provisioner_response['subnet']['gateway_ip'])
