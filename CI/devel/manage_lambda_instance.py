import argparse
import requests
import time
from pprint import pprint

from kamaki.clients.utils import https

from utils import VMInfo


class LambdaInstanceManager:
    def __init__(self, authentication_token=None, service_vm_name=None):
        https.patch_ignore_ssl()

        self.authentication_token = authentication_token
        self.service_vm_name = service_vm_name

        vm_info = VMInfo(self.authentication_token, self.service_vm_name)
        self.service_vm_ip = vm_info.vm_ip

        self.lambda_instance_information = {'project_name': "lambda.grnet.gr",
                                            'instance_name': "Lambda Instance CI",
                                            'network_request': 1,
                                            'master_name': "Lambda Master CI",
                                            'vcpus_master': 4,
                                            'vcpus_slave': 4,
                                            'ram_master': 4096,
                                            'ram_slave': 4096,
                                            'disk_master': 20,
                                            'disk_slave': 20,
                                            'slaves': 2,
                                            'ip_allocation': "master"}

    def create(self):
        # Send a request to the service vm to create a lambda instance.
        response = requests.post("http://{ip}/api/lambda-instance/".format(ip=self.service_vm_ip),
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': "Token {token}".
                                 format(token=self.authentication_token)},
                                 json=self.lambda_instance_information)

        # Print the response for logging purposes.
        response_json = response.json()
        pprint(response_json)

        # Keep the id of the lambda instance that will be created.
        lambda_instance_uuid = response_json['data'][0]['id']

        # Wait until the entry of the lambda instance on the API database has been created.
        lambda_instances = requests.get("http://{ip}/api/lambda-instances/".
                                        format(ip=self.service_vm_ip),
                                               headers={'Authorization': "Token {token}".
                                                        format(token=self.authentication_token)})
        while len(lambda_instances.json()['data']) == 0:
            lambda_instances = requests.\
                get("http://{ip}/api/lambda-instances/".format(ip=self.service_vm_ip),
                    headers={'Authorization': "Token {token}".
                    format(token=self.authentication_token)})

        # Wait for the lambda instance to be created and started.
        self._wait_for_lambda_instance_status("STARTED", lambda_instance_uuid)

    def destroy(self):
        lambda_instances = requests.get("http://{ip}/api/lambda-instances/".
                                               format(ip=self.service_vm_ip),
                                               headers={'Authorization': "Token {token}".
                                                        format(token=self.authentication_token)})
        lambda_instance_uuid = lambda_instances.json()['data'][0]['id']

        # Send a request to the service vm to destroy the lambda instance.
        requests.delete("http://{ip}/api/lambda-instances/{id}/".
                        format(ip=self.service_vm_ip, id=lambda_instance_uuid),
                        headers={'Authorization': "Token {token}".
                                 format(token=self.authentication_token)})

        # Wait for the lambda instance to be destroyed.
        self._wait_for_lambda_instance_status("DESTROYED", lambda_instance_uuid, 60, 5)

    def _wait_for_lambda_instance_status(self, status, lambda_instance_uuid,
                                         sleep_time=300, max_wait=20):
        lambda_instance_details = requests.get("http://{ip}/api/lambda-instances/{id}/".
                                               format(ip=self.service_vm_ip,
                                                      id=lambda_instance_uuid),
                                               headers={'Authorization': "Token {token}".
                                                        format(token=self.authentication_token)})
        lambda_instance_status = lambda_instance_details.json()['data'][0]['status']['message']
        pprint("Lambda Instance status is {lambda_instance_status}. Waiting...".
               format(lambda_instance_status=lambda_instance_status))

        while lambda_instance_status != status and max_wait > 0:
            time.sleep(sleep_time)
            lambda_instance_details = requests.get("http://{ip}/api/lambda-instances/{id}/".
                                                   format(ip=self.service_vm_ip,
                                                          id=lambda_instance_uuid),
                                                   headers={'Authorization': "Token {token}".
                                                            format(token=self.
                                                                   authentication_token)})
            lambda_instance_status = lambda_instance_details.json()['data'][0]['status']['message']
            pprint("Lambda Instance status is {lambda_instance_status}. Waiting...".
                   format(lambda_instance_status=lambda_instance_status))
            max_wait -= 1


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description='Manage Lambda Instance')
    argument_parser.add_argument('--action', type=str, required=True, dest='action',
                                 choices=['create', 'destroy'])
    argument_parser.add_argument('--service_vm_name', type=str, required=True,
                                 dest='service_vm_name')
    argument_parser.add_argument('--auth_token', type=str, required=True, dest='auth_token')
    arguments = argument_parser.parse_args()

    lambda_instance_manager = LambdaInstanceManager(arguments.auth_token, arguments.service_vm_name)

    if arguments.action == 'create':
        lambda_instance_manager.create()
    elif arguments.action == 'destroy':
        lambda_instance_manager.destroy()
