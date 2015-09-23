from kamaki.clients import ClientError
import logging
from fokia.provisioner_base import ProvisionerBase
from fokia.cluster_error_constants import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VMProvisioner(ProvisionerBase):

    def __init__(self, auth_token, cloud_name=None):
        super(VMProvisioner, self).__init__(auth_token=auth_token, cloud_name=cloud_name)

    def create_central_vm(self, vm_name, wait=True, **kwargs):

        quotas = self.get_quotas()
        project_id = self.find_project_id(**kwargs)['id']
        response = self.check_all_resources(quotas,
                                            vcpus=kwargs['vcpus'],
                                            ram=kwargs['ram'],
                                            disk=kwargs['disk'],
                                            project_name=kwargs['project_name'])

        if response:

            # Check flavors for VM
            flavor = self.find_flavor(vcpus=kwargs['vcpus_master'],
                                      ram=kwargs['ram_master'],
                                      disk=kwargs['disk_master'])
            if not flavor:
                msg = 'This flavor does not allow create.'
                raise ClientError(msg, error_flavor_list)

            public_ip = self.reserve_ip(project_id=project_id)

            vm = self.create_vm(vm_name=vm_name,
                                ip=public_ip,
                                flavor=flavor,
                                **kwargs)

            # Wait for VM to complete being built
            if wait:
                self.cyclades.wait_server(server_id=vm['id'])

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
        available_cyclades_disk_GB = (limit_cd - usage_cd - pending_cd) / self.Bytes_to_GB
        if available_cyclades_disk_GB < kwargs['disk']:
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
        if available_ips:
            msg = 'authorized IPs out of limit'
            raise ClientError(msg, error_get_ip)
        return True


class CentralServiceManager:
    """
    Class deploying dynamically the central service VM.
    It uses the kamaki API to create/destroy the actual vm, running on
    the ~okeanos infrastructure.
    """

    def central_service_create(self):
        """
        Creates the central service vm and installs the relevant s/w.
        :return:
        """
        raise NotImplementedError

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
