import argparse

from kamaki.clients.astakos import AstakosClient
from kamaki.clients.cyclades import CycladesComputeClient, CycladesNetworkClient
from kamaki.clients.utils import https

class VMInfo:
    AUTHENTICATION_URL = 'https://accounts.okeanos.grnet.gr/identity/v2.0'

    def __init__(self, authentication_token=None, vm_name=None):
        https.patch_ignore_ssl()

        self.authentication_token = authentication_token
        self.vm_name = vm_name

        self._get_vm_id_by_name()
        self._get_vm_ip_by_id()

    def _get_vm_id_by_name(self):
        # Create cyclades compute client.
        cyclades_compute_url = AstakosClient(self.AUTHENTICATION_URL, self.authentication_token).\
            get_endpoint_url(CycladesComputeClient.service_type)
        cyclades_compute_client = CycladesComputeClient(cyclades_compute_url,
                                                        self.authentication_token)
    
        # Get the id of the vm with the specified name.
        servers = cyclades_compute_client.list_servers()
    
        self.vm_id = None
        for server in servers:
            if server['name'] == self.vm_name:
                self.vm_id = server['id']
                break

        return self.vm_id

    def _get_vm_ip_by_id(self):
        # Create cyclades network client.
        cyclades_network_url = AstakosClient(self.AUTHENTICATION_URL, self.authentication_token).\
            get_endpoint_url(CycladesNetworkClient.service_type)
        cyclades_network_client = CycladesNetworkClient(cyclades_network_url,
                                                        self.authentication_token)

        # Get the ip of the vm with the specified id.
        floating_ips = cyclades_network_client.list_floatingips()

        self.vm_ip = None
        for floating_ip in floating_ips:
            if floating_ip['instance_id'] == "{vm_id}".format(vm_id=self.vm_id):
                self.vm_ip = floating_ip['floating_ip_address']
                break

        return self.vm_ip


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description='Manage Lambda Instance')
    argument_parser.add_argument('--get', type=str, required=True, dest='get',
                                 choices=['ip', 'id'])
    argument_parser.add_argument('--vm_name', type=str, required=True,
                                 dest='vm_name')
    argument_parser.add_argument('--auth_token', type=str, required=True, dest='auth_token')
    arguments = argument_parser.parse_args()

    vm_info = VMInfo(arguments.auth_token, arguments.vm_name)

    if arguments.get == 'ip':
        print vm_info.vm_ip
    elif arguments.get == 'id':
        print vm_info.vm_id
