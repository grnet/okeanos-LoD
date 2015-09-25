from kamaki.clients import ClientError
from fokia.provisioner_base import ProvisionerBase
from fokia.cluster_error_constants import *
from base64 import b64encode

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VM_Manager(ProvisionerBase):
    def __init__(self, auth_token, cloud_name=None):
        super(VM_Manager, self).__init__(auth_token=auth_token, cloud_name=cloud_name)

    def create_single_vm(self, vm_name, wait=True, **kwargs):
        """
        Creates a single VM
        :return: vm id
        """
        quotas = self.get_quotas()
        project_id = self.find_project_id(**kwargs)['id']
        response = self.check_all_resources(quotas,
                                            vcpus=kwargs['vcpus'],
                                            ram=kwargs['ram'],
                                            disk=kwargs['disk'],
                                            project_name=kwargs['project_name'])

        if response:

            # Check flavors for VM
            flavor = self.find_flavor(vcpus=kwargs['vcpus'],
                                      ram=kwargs['ram'],
                                      disk=kwargs['disk'])
            if not flavor:
                msg = 'This flavor does not allow create.'
                raise ClientError(msg, error_flavor_list)

            public_ip = self.reserve_ip(project_id=project_id)

            with open(os.path.expanduser('~/.ssh/id_rsa.pub'), 'r') as public_key_file:
                public_key = public_key_file.read()
            authorized = {'contents': b64encode(public_key),
                          'path': '/root/.ssh/authorized_keys',
                          'owner': 'root', 'group': 'root', 'mode': 0600}

            vm = self.create_vm(vm_name=vm_name,
                                ip=public_ip,
                                personality=[authorized],
                                flavor=flavor,
                                **kwargs)

            server_id = vm['id']

            # Wait for VM to complete being built
            if wait:
                self.cyclades.wait_server(server_id=server_id)

            return server_id

        return

    def check_all_resources(self, quotas, **kwargs):
        """
        Checks user's quota for every requested resource.
        Returns True if everything available.
        :param **kwargs: arguments
        """
        project_id = self.find_project_id(**kwargs)['id']
        # Check for VM
        pending_vm = quotas[project_id]['cyclades.vm']['project_pending']
        limit_vm = quotas[project_id]['cyclades.vm']['project_limit']
        usage_vm = quotas[project_id]['cyclades.vm']['project_usage']
        available_vm = limit_vm - usage_vm - pending_vm
        if available_vm < 1:
            msg = 'Cyclades VMs out of limit'
            raise ClientError(msg, error_quotas_cluster_size)
        # Check for CPUs
        pending_cpu = quotas[project_id]['cyclades.cpu']['project_pending']
        limit_cpu = quotas[project_id]['cyclades.cpu']['project_limit']
        usage_cpu = quotas[project_id]['cyclades.cpu']['project_usage']
        available_cpu = limit_cpu - usage_cpu - pending_cpu
        if available_cpu < kwargs['vcpus']:
            msg = 'Cyclades cpu out of limit'
            raise ClientError(msg, error_quotas_cpu)
        # Check for RAM
        pending_ram = quotas[project_id]['cyclades.ram']['project_pending']
        limit_ram = quotas[project_id]['cyclades.ram']['project_limit']
        usage_ram = quotas[project_id]['cyclades.ram']['project_usage']
        available_ram = (limit_ram - usage_ram - pending_ram) / self.Bytes_to_MB
        if available_ram < kwargs['ram']:
            msg = 'Cyclades ram out of limit'
            raise ClientError(msg, error_quotas_ram)
        # Check for Disk space
        pending_cd = quotas[project_id]['cyclades.ram']['project_pending']
        limit_cd = quotas[project_id]['cyclades.disk']['project_limit']
        usage_cd = quotas[project_id]['cyclades.disk']['project_usage']
        available_cyclades_disk_gb = (limit_cd - usage_cd - pending_cd) / self.Bytes_to_GB
        if available_cyclades_disk_gb < kwargs['disk']:
            msg = 'Cyclades disk out of limit'
            raise ClientError(msg, error_quotas_cyclades_disk)
        # Check for authorized IPs
        pending_ips = quotas[project_id]['cyclades.floating_ip']['project_pending']
        limit_ips = quotas[project_id]['cyclades.floating_ip']['project_limit']
        usage_ips = quotas[project_id]['cyclades.floating_ip']['project_usage']
        available_ips = limit_ips - usage_ips - pending_ips
        # TODO: figure out how to handle unassigned floating ips
        # for d in list_float_ips:
        #     if d['instance_id'] is None and d['port_id'] is None:
        #         available_ips += 1
        if available_ips < 1:
            msg = 'authorized IPs out of limit'
            raise ClientError(msg, error_get_ip)
        return True

    def destroy(self, vm_id, public_ip_id=None):
        """
        Destroys a single VM
        :return:
        """
        # Get the current status of the VM
        vm_status = self.cyclades.get_server_details(vm_id)["status"]

        # Destroy the VM
        if vm_status != "DELETED":
            self.cyclades.delete_server(vm_id)

        # Wait for the VM to be destroyed before destroying the public ip
            self.cyclades.wait_server(vm_id, current_status=vm_status, max_wait=600)

        # Destroy the public ip, if it exists
        if public_ip_id is not None:
            self.network_client.delete_floatingip(public_ip_id)

    def start(self, vm_id):
        """
        Starts a single VM
        :return:
        """
        self.cyclades.start_server(vm_id)

    def stop(self, vm_id):
        """
        Stops a single VM
        :return:
        """
        self.cyclades.shutdown_server(vm_id)
