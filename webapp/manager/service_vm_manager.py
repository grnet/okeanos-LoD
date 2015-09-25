import logging
from fokia.vm_manager import VM_Manager
from fokia.ansible_manager_minimal import Manager
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

    def service_vm_create(self, vcpus=4, ram=4096, disk=40,
                          project_name='lambda.grnet.gr',
                          private_key_path=None, public_key_path=None):
        """
        Creates the service vm and installs the relevant s/w.
        :return: ansible result
        """

        provisioner = VM_Manager(auth_token=self.auth_token)
        vm_name = 'Service VM'
        vm_id = provisioner.create_single_vm(vm_name=vm_name,
                                             vcpus=vcpus, ram=ram, disk=disk,
                                             project_name=project_name,
                                             public_key_path=public_key_path)
        hostname = 'snf-' + str(vm_id) + '.vm.okeanos.grnet.gr'
        group = 'service-vms'
        ansible_manager = Manager(hostname, group, private_key_path)
        ansible_result = ansible_manager.run_playbook(
            playbook_file=os.path.join(ansible_path, 'playbooks', 'setup.yml'))
        return ansible_result

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
