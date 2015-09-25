import logging
from fokia.vm_provisioner import VM_Provisioner
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
        provisioner = VM_Provisioner(auth_token=auth_token)
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

    def central_service_destroy(self):
        """
        Deletes the central service vm.
        :return:
        """
        raise NotImplementedError

    def central_service_start(self):
        """
        Starts the central service vm if it's not running.
        :return:
        """
        raise NotImplementedError

    def central_service_stop(self):
        """
        Stops the central service vm if it's running.
        :return:
        """
        raise NotImplementedError
