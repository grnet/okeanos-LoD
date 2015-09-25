import logging
from fokia.vm_manager import VM_Manager
from fokia.ansible_manager_minimal import Manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CentralServiceManager:
    """
    Class deploying dynamically the central service VM.
    It uses the kamaki API to create/destroy the actual vm, running on
    the ~okeanos infrastructure.
    """

    def central_service_create(self, auth_token):
        """
        Creates the central service vm and installs the relevant s/w.
        :return:
        """
        provisioner = VM_Manager(auth_token=auth_token)
        vm_name = 'central_service'
        vcpus = 4
        ram = 4096
        disk = 40
        project_name = 'lambda.grnet.gr'
        server_id = provisioner.create_single_vm(vm_name=vm_name,
                                                 vcpus=vcpus, ram=ram, disk=disk,
                                                 project_name=project_name)
        hostname = 'snf-' + str(server_id) + '.vm.okeanos.grnet.gr'
        group = 'central-vm'
        ansible_manager = Manager(hostname, group)
        ansible_result = ansible_manager.run_playbook(
            playbook_file='../../central_service/ansible/playbooks/setup.yml')
        return ansible_result

    def central_service_destroy(self, auth_token, vm_id, public_ip_id):
        """
        Deletes the central service vm.
        :return:
        """
        vmmanager = VM_Manager(auth_token=auth_token)
        vmmanager.destroy(vm_id=vm_id, public_ip_id=public_ip_id)

    def central_service_start(self, auth_token, vm_id):
        """
        Starts the central service vm if it's not running.
        :return:
        """
        vmmanager = VM_Manager(auth_token=auth_token)
        vmmanager.start(vm_id=vm_id)

    def central_service_stop(self, auth_token, vm_id):
        """
        Stops the central service vm if it's running.
        :return:
        """
        vmmanager = VM_Manager(auth_token=auth_token)
        vmmanager.stop(vm_id=vm_id)
