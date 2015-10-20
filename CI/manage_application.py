import argparse
import requests
import time
from pprint import pprint

from kamaki.clients.utils import https

from utils import VMInfo


class ApplicationManager:
    """
    Class to manage an application for the ~okeanos LoD Service.
    Contains methods to upload an application to Pithos storage, deploy an application on a Lambda
    Instance and start a deployed application. Every interaction is done through the ~okeanos LoD
    Service API.
    """

    def __init__(self, authentication_token=None, service_vm_name=None, application=None):
        https.patch_ignore_ssl()

        self.authentication_token = authentication_token
        self.service_vm_name = service_vm_name
        self.application = application

        vm_info = VMInfo(self.authentication_token, self.service_vm_name)
        self.service_vm_ip = vm_info.vm_ip

    def upload(self, sleep_time=10, max_wait=6):
        """
        Method for uploading an application to Pithos storage.
        :param sleep_time: Time(in milli seconds) to sleep while waiting for the application
                           database entry to be create on ~okeanos LoD Service API.
        :param max_wait: Number of iterations to wait for the application database entry to be
                         created on ~okeanos LoD Service API.
        """

        # Send a request to the service vm to upload the application.
        with open(self.application, 'r') as application_file:
            response = requests.post("http://{ip}/api/apps/".format(ip=self.service_vm_ip),
                                     headers={'Authorization': "Token {token}".
                                     format(token=self.authentication_token)},
                                     files={'file': application_file},
                                     data={'description': "Stream Word Count",
                                           'project_name': "lambda.grnet.gr",
                                           'type': "streaming"})

        # Print the response for logging purposes.
        response_json = response.json()
        pprint(response_json)

        # Keep the id of the application that will be created.
        application_uuid = response_json['data'][0]['id']

        # Wait until the entry of the application on the API database has been created.
        applications = requests.get("http://{ip}/api/apps/".format(ip=self.service_vm_ip),
                                    headers={'Authorization': "Token {token}".
                                             format(token=self.authentication_token)})
        while len(applications.json()['data']) == 0 and max_wait > 0:
            time.sleep(sleep_time)
            applications = requests.get("http://{ip}/api/apps/".format(ip=self.service_vm_ip),
                                        headers={'Authorization': "Token {token}".
                                                 format(token=self.authentication_token)})
            max_wait -= 1

        # Wait for the application to be uploaded.
        self._wait_for_application_status("UPLOADED", application_uuid)

    def deploy(self, sleep_time=10, max_wait=6):
        """
        Method for deploying an application to a Lambda Instance.
        :param sleep_time: Time(in milli seconds) to sleep waiting for the application to be
                           deployed.
        :param max_wait: Number of iterations to wait for the application to be deployed.
        """

        # Get the uuid of the lambda instance.
        lambda_instances = requests.get("http://{ip}/api/lambda-instances/".
                                        format(ip=self.service_vm_ip),
                                        headers={'Authorization': "Token {token}".
                                                 format(token=self.authentication_token)})
        lambda_instance_uuid = lambda_instances.json()['data'][0]['id']

        # Get the uuid of the application.
        applications = requests.get("http://{ip}/api/apps/".format(ip=self.service_vm_ip),
                                    headers={'Authorization': "Token {token}".
                                             format(token=self.authentication_token)})
        application_uuid = applications.json()['data'][0]['id']

        # Send a request to the service vm to deploy the application.
        requests.post("http://{ip}/api/apps/{application_id}/deploy/".
                      format(ip=self.service_vm_ip, application_id=application_uuid),
                      headers={'Authorization': "Token {token}".
                               format(token=self.authentication_token)},
                      json={'lambda_instance_id': lambda_instance_uuid})

        # Wait for the application to be deployed.
        application_details = requests.get("http://{ip}/api/apps/{id}/".
                                           format(ip=self.service_vm_ip, id=application_uuid),
                                           headers={'Authorization': "Token {token}".
                                                    format(token=self.authentication_token)})
        while len(application_details.json()['data'][0]['applications']) == 0 and max_wait > 0:
            time.sleep(sleep_time)
            application_details = requests.get("http://{ip}/api/apps/{id}/".
                                               format(ip=self.service_vm_ip, id=application_uuid),
                                               headers={'Authorization': "Token {token}".
                                                        format(token=self.authentication_token)})
            max_wait -= 1

    def start(self, sleep_time=10, max_wait=6):
        """
        Method for starting an application on a Lambda Instance.
        :param sleep_time: Time(in milli seconds) to sleep waiting for the application to be
                           started.
        :param max_wait: Number of iterations to wait for the application to be started.
        """

        # Get the uuid of the lambda instance.
        lambda_instances = requests.get("http://{ip}/api/lambda-instances/".
                                        format(ip=self.service_vm_ip),
                                        headers={'Authorization': "Token {token}".
                                                 format(token=self.authentication_token)})
        lambda_instance_uuid = lambda_instances.json()['data'][0]['id']

        # Get the uuid of the application.
        applications = requests.get("http://{ip}/api/apps/".format(ip=self.service_vm_ip),
                                    headers={'Authorization': "Token {token}".
                                             format(token=self.authentication_token)})
        application_uuid = applications.json()['data'][0]['id']

        # Send a request to the service vm to start the application.
        requests.post("http://{ip}/api/apps/{application_id}/start/".
                      format(ip=self.service_vm_ip, application_id=application_uuid),
                      headers={'Authorization': "Token {token}".
                               format(token=self.authentication_token)},
                      json={'lambda_instance_id': lambda_instance_uuid})

        # Wait for the application to be started.
        application_details = requests.get("http://{ip}/api/apps/{id}/".
                                           format(ip=self.service_vm_ip, id=application_uuid),
                                           headers={'Authorization': "Token {token}".
                                                    format(token=self.authentication_token)})
        while (not application_details.json()['data'][0]['applications'][0]['started'])\
                and (max_wait > 0):
            time.sleep(sleep_time)
            application_details = requests.get("http://{ip}/api/apps/{id}/".
                                               format(ip=self.service_vm_ip, id=application_uuid),
                                               headers={'Authorization': "Token {token}".
                                                        format(token=self.authentication_token)})
            max_wait -= 1

    def _wait_for_application_status(self, status, application_uuid, sleep_time=60, max_wait=5):
        """
        Helper method. Waits for a specified amount of time or until a current state of an
                          application is reached.
        :param status: The status of the application to be reached.
        :param application_uuid: The uuid of the application.
        :param sleep_time: Time(in milli seconds) to sleep waiting for the application to reach
                           the specified state.
        :param max_wait: Number of iterations to wait for the application to reach the specified
                         state.
        """

        application_details = requests.get("http://{ip}/api/apps/{id}/".
                                           format(ip=self.service_vm_ip, id=application_uuid),
                                           headers={'Authorization': "Token {token}".
                                                    format(token=self.authentication_token)})
        application_status = application_details.json()['data'][0]['status']['message']
        pprint("Application status is {application_status}. Waiting...".
               format(application_status=application_status))

        while application_status != status and max_wait > 0:
            time.sleep(sleep_time)
            application_details = requests.get("http://{ip}/api/apps/{id}/".
                                               format(ip=self.service_vm_ip, id=application_uuid),
                                               headers={'Authorization': "Token {token}".
                                                        format(token=self.authentication_token)})
            application_status = application_details.json()['data'][0]['status']['message']
            pprint("Application status is {application_status}. Waiting...".
                   format(application_status=application_status))
            max_wait -= 1


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description='Manage Application')
    argument_parser.add_argument('--action', type=str, required=True, dest='action',
                                 choices=['upload', 'deploy', 'start'])
    argument_parser.add_argument('--service_vm_name', type=str, required=True,
                                 dest='service_vm_name')
    argument_parser.add_argument('--application', type=str, required=False,
                                 dest='application')
    argument_parser.add_argument('--auth_token', type=str, required=True, dest='auth_token')
    arguments = argument_parser.parse_args()

    application_manager = ApplicationManager(arguments.auth_token, arguments.service_vm_name,
                                             arguments.application)

    if arguments.action == 'upload':
        application_manager.upload()
    elif arguments.action == 'deploy':
        application_manager.deploy()
    elif arguments.action == 'start':
        application_manager.start()
