import logging
import argparse
from fokia.vm_manager import VM_Manager
from fokia.ansible_manager_minimal import Manager
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

check_folders = ['/var/www/okeanos-LoD/central_service/ansible',
                 'okeanos-LoD/central_service/ansible',
                 'central_service/ansible',
                 '../central_service/ansible',
                 '../../central_service/ansible']

ansible_path = os.environ.get('CENTRAL_ANSIBLE_PATH', None)
if not ansible_path:
    for folder in check_folders:
        if os.path.exists(folder):
            ansible_path = folder
            break


class CentralServiceManager(object):
    """
    Class deploying the central service VM dynamically.
    It uses the kamaki API to create/destroy the actual VM, running on
    the ~okeanos infrastructure. It uses ansible to install and configure
    the required packages and services.
    """

    def __init__(self, auth_token):
        self.auth_token = auth_token

    def central_service_create(self, vm_name='Central Service',
                               vcpus=4, ram=4096, disk=40,
                               project_name=None,
                               private_key_path=None, public_key_path=None):
        """
        Creates the central service vm and installs the relevant s/w.
        :return: ansible result
        """

        provisioner = VM_Manager(auth_token=self.auth_token)
        vm_id = provisioner.create_single_vm(vm_name=vm_name,
                                             vcpus=vcpus, ram=ram, disk=disk,
                                             project_name=project_name,
                                             public_key_path=public_key_path)
        hostname = 'snf-' + str(vm_id) + '.vm.okeanos.grnet.gr'
        group = 'central-vm'
        ansible_manager = Manager(hostname, group, private_key_path)
        ansible_result = ansible_manager.run_playbook(
            playbook_file=os.path.join(ansible_path, 'playbooks', 'setup.yml'))
        return ansible_result

    def central_service_destroy(self, vm_id):
        """
        Deletes the central service vm.
        :return:
        """

        vmmanager = VM_Manager(auth_token=self.auth_token)
        vmmanager.destroy(vm_id=vm_id)

    def central_service_start(self, vm_id):
        """
        Starts the central service vm if it's not running.
        :return:
        """

        vmmanager = VM_Manager(auth_token=self.auth_token)
        vmmanager.start(vm_id=vm_id)

    def central_service_stop(self, vm_id):
        """
        Stops the central service vm if it's running.
        :return:
        """

        vmmanager = VM_Manager(auth_token=self.auth_token)
        vmmanager.stop(vm_id=vm_id)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Central service VM provisioning')
    parser.add_argument('--action', type=str, dest='action', required=True,
                        choices=['create', 'start', 'stop', 'destroy'],
                        help="action to be performed")
    parser.add_argument('--auth-token', type=str, dest='auth_token', required=False,
                        help="the ~okeanos authentication token of the user")
    parser.add_argument('--vm-id', type=int, dest='vm_id',
                        help="the ~okeanos id of the correspoding VM")
    parser.add_argument('--vm-name', type=str, dest='vm_name', required=False,
                        default='Central Service', help="the name of the VM")
    parser.add_argument('--vcpus', type=int, dest='vcpus', default='4',
                        choices=[1, 2, 4, 8], help="the number of CPUs on the VM")
    parser.add_argument('--ram', type=int, dest='ram', default='4096',
                        choices=[512, 1024, 2048, 4096, 6144, 8192],
                        help="the amount of RAM on the VM")
    parser.add_argument('--disk', type=int, dest='disk', default='40',
                        choices=[5, 10, 20, 40, 60, 80, 100], help="the size of the HDD on the VM")
    parser.add_argument('--project-name', type=str, dest='project_name',
                        help="the ~okeanos project with the appropriate quotas for the VM")
    parser.add_argument('--private-key-path', type=str, dest='private_key_path',
                        help="path to private ssh key to be used by Ansible"
                             " (should pair with the provided public key)")
    parser.add_argument('--public-key-path', type=str, dest='public_key_path',
                        help="path to public ssh key to be injected in the VM"
                             " (should pair with the provided private key)")
    args = parser.parse_args()

    csm = CentralServiceManager(args.auth_token)
    if args.action == 'create':
        csm.central_service_create(vm_name=args.vm_name,
                                   vcpus=args.vcpus, ram=args.ram, disk=args.disk,
                                   project_name=args.project_name,
                                   private_key_path=args.private_key_path,
                                   public_key_path=args.public_key_path)
    elif args.vm_id is None:
        raise ValueError("VM id must be specified")
    else:
        if args.action == 'start':
            csm.central_service_start(vm_id=args.vm_id)
        elif args.action == 'stop':
            csm.central_service_stop(vm_id=args.vm_id)
        elif args.action == 'destroy':
            csm.central_service_destroy(vm_id=args.vm_id)
