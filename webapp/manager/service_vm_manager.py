import logging
import argparse
from fokia.vm_manager import VM_Manager
from fokia.ansible_manager_minimal import Manager
from fokia.utils import check_auth_token
from kamaki.cli.config import Config as KamakiConfig
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

check_folders = ['/var/www/okeanos-LoD/webapp/ansible',
                 'okeanos-LoD/webapp/ansible',
                 'webapp/ansible',
                 '../webapp/ansible',
                 '../../webapp/ansible']

ansible_path = os.environ.get('SERVICE_ANSIBLE_PATH', None)
if not ansible_path:
    for folder in check_folders:
        if os.path.exists(folder):
            ansible_path = folder
            break


class ServiceVMManager(object):
    """
    Class deploying the service VM dynamically.
    It uses the kamaki API to create/destroy the actual VM, running on
    the ~okeanos infrastructure. It uses ansible to install and configure
    the required packages and services.
    """

    def __init__(self, auth_token):
        self.auth_token = auth_token

    def service_vm_create(self, vm_name='Service VM',
                          vcpus=4, ram=4096, disk=40,
                          project_name=None,
                          private_key_path=None, public_key_path=None,
                          only_tags=None, skip_tags=None):
        """
        Creates the service vm and installs the relevant s/w.
        :return: ansible result
        """

        provisioner = VM_Manager(auth_token=self.auth_token)
        vm_id = provisioner.create_single_vm(vm_name=vm_name,
                                             vcpus=vcpus, ram=ram, disk=disk,
                                             project_name=project_name,
                                             public_key_path=public_key_path)
        hostname = 'snf-' + str(vm_id) + '.vm.okeanos.grnet.gr'
        group = 'service-vms'

        self._patch_auth_token_ansible()
        ansible_manager = Manager(hostname, group, private_key_path)
        ansible_result = ansible_manager.run_playbook(
            playbook_file=os.path.join(ansible_path, 'playbooks', 'setup.yml'),
            only_tags=only_tags, skip_tags=skip_tags)

        self._clean_up_token_ansible_patch()
        return ansible_result

    def _patch_auth_token_ansible(self):
        if self.auth_token is None:
            # Load .kamakirc configuration
            logger.info("Retrieving .kamakirc configuration")
            self.config = KamakiConfig()
            if not os.path.exists(self.config.path):
                raise IOError('No auth token given, and .kamakirc does not exist! Aborting.')
            cloud_section = self.config._sections['cloud'].get(self.config.get('global',
                                                                               'default_cloud'))
            if not cloud_section:
                message = "Default Cloud was not found in your .kamakirc configuration file. " \
                          "Currently you have available in your configuration these clouds: %s"
                raise KeyError(message % (self.config._sections['cloud'].keys()))

            # Get the authentication token
            self.auth_token = cloud_section['token']

        res, info = check_auth_token(self.auth_token)
        uuid = None
        if res:
            uuid = info['access']['user']['id']
        with open("../ansible/roles/service-vm/vars/main.yml", "a") as vars_file:
            vars_file.write("user_uuid: {user_uuid}\n".format(user_uuid=uuid))

    def _clean_up_token_ansible_patch(self):
        file_lines = None
        with open("../ansible/roles/service-vm/vars/main.yml", "r") as vars_file:
            file_lines = vars_file.readlines()
        with open("../ansible/roles/service-vm/vars/main.yml", "w") as vars_file:
            vars_file.writelines([item for item in file_lines[:-1]])

    def service_vm_destroy(self, vm_id):
        """
        Deletes the service vm.
        :return:
        """

        vmmanager = VM_Manager(auth_token=self.auth_token)
        vmmanager.destroy(vm_id=vm_id)

    def service_vm_start(self, vm_id):
        """
        Starts the service vm if it's not running.
        :return:
        """

        vmmanager = VM_Manager(auth_token=self.auth_token)
        vmmanager.start(vm_id=vm_id)

    def service_vm_stop(self, vm_id):
        """
        Stops the service vm if it's running.
        :return:
        """

        vmmanager = VM_Manager(auth_token=self.auth_token)
        vmmanager.stop(vm_id=vm_id)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Lambda service VM provisioning')
    parser.add_argument('--action', type=str, dest='action', required=True,
                        choices=['create', 'start', 'stop', 'destroy', 'image_creation'])
    parser.add_argument('--auth-token', type=str, dest='auth_token', required=False)
    parser.add_argument('--vm-id', type=int, dest='vm_id')
    parser.add_argument('--vm-name', type=str, dest='vm_name', required=False,
                        default="Service VM")
    parser.add_argument('--vcpus', type=int, dest='vcpus', default='4',
                        choices=[1, 2, 4, 8])
    parser.add_argument('--ram', type=int, dest='ram', default='4096',
                        choices=[512, 1024, 2048, 4096, 6144, 8192])
    parser.add_argument('--disk', type=int, dest='disk', default='40',
                        choices=[5, 10, 20, 40, 60, 80, 100])
    parser.add_argument('--project-name', type=str, dest='project_name')
    parser.add_argument('--private-key-path', type=str, dest='private_key_path')
    parser.add_argument('--public-key-path', type=str, dest='public_key_path')
    args = parser.parse_args()

    sm = ServiceVMManager(args.auth_token)
    if args.action == 'create':
        sm.service_vm_create(vm_name=args.vm_name,
                             vcpus=args.vcpus, ram=args.ram, disk=args.disk,
                             project_name=args.project_name,
                             private_key_path=args.private_key_path,
                             public_key_path=args.public_key_path)
    elif args.action == 'image_creation':
        sm.service_vm_create(vm_name=args.vm_name,
                             vcpus=args.vcpus, ram=args.ram, disk=args.disk,
                             project_name=args.project_name,
                             private_key_path=args.private_key_path,
                             public_key_path=args.public_key_path,
                             skip_tags=['image-configure', 'create-user'])
    elif args.vm_id is None:
        raise ValueError("VM id must be specified")
    else:
        if args.action == 'start':
            sm.service_vm_start(vm_id=args.vm_id)
        elif args.action == 'stop':
            sm.service_vm_stop(vm_id=args.vm_id)
        elif args.action == 'destroy':
            sm.service_vm_destroy(vm_id=args.vm_id)
