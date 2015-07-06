#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import logging
import argparse
from cluster_error_constants import *
from kamaki.clients import astakos, cyclades
from kamaki.clients import ClientError
from kamaki.clients.utils import https
from kamaki.cli.config import Config as KamakiConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: remove this and actually use ssl cert files
https.patch_ignore_ssl()


storage_templates = ['drdb', 'ext_vlmc']


class Provisioner:
    """
        provisions virtual machines on ~okeanos
    """

    def __init__(self, cloud_name):

        # Load .kamakirc configuration
        self.config = KamakiConfig()
        cloud_section = self.config._sections['cloud'].get(cloud_name)
        if not cloud_section:
            message = "Cloud '%s' was not found in you .kamakirc configuration file. " \
                      "Currently you have availablie in your configuration these clouds: %s"
            raise KeyError(message % (cloud_name, self.config._sections['cloud'].keys()))

        # Get the authentication url and token
        auth_url, auth_token = cloud_section['url'], cloud_section['token']

        # Create the astakos client
        self.astakos = astakos.AstakosClient(auth_url, auth_token)

        # Create the cyclades client
        computeURL = self.astakos.get_endpoint_url(
            cyclades.CycladesComputeClient.service_type)
        self.cyclades = cyclades.CycladesComputeClient(computeURL, auth_token)

        # Create the identity_client
        self.identity_client = astakos.AstakosClient(auth_url, auth_token)

        # Create the network client
        networkURL = self.identity_client.get_endpoint_url(
            cyclades.CycladesNetworkClient.service_type)
        self.network_client = cyclades.CycladesNetworkClient(networkURL, auth_token)

        # Constants
        self.Bytes_to_GB = 1024*1024*1024
        self.Bytes_to_MB = 1024*1024

    def find_flavor(self, **kwargs):
        """
        :param kwargs: should contains the keys that specify the specs
        :return: first flavor objects that matches the specs criteria
        """

        # Set all the default parameters
        kwargs.setdefault("vcpus", 1)
        kwargs.setdefault("ram", 1024)
        kwargs.setdefault("disk", 40)

        for flavor in self.cyclades.list_flavors(detail=True):
            if all([kwargs[key] == flavor[key]
                    for key in set(flavor.keys()).intersection(kwargs.keys())]):
                return flavor
        return None

    def find_image(self, **kwargs):
        """
        :param image_name: Name of the image to filter by
        :param kwargs:
        :return: first image object that matches the name criteria
        """
        image_name = kwargs['image_name']
        for image in self.cyclades.list_images(detail=True):
            if image_name in image['name']:
                return image
        return None

    def find_project_id(self, **kwargs):
        """
        :param kwargs: name, state, owner and mode to filter project by
        :return: first project_id that matches the project name
        """
        filter = {
            'name': kwargs.get("project_name"),
            'state': kwargs.get("project_state"),
            'owner': kwargs.get("project_owner"),
            'mode': kwargs.get("project_mode"),
        }
        return self.astakos.get_projects(**filter)[0]

    def create_vm(self, vm_name=None, **kwargs):
        """
        :param vm_name: Name of the virtual machine to create
        :param kwargs: passed to the functions called for detail options
        :return:
        """
        flavor_id = self.find_flavor(**kwargs)['id']
        image_id = self.find_image(**kwargs)['id']
        project_id = self.find_project_id(**kwargs)['id']
        try:
            okeanos_response = self.cyclades.create_server(name=vm_name, flavor_id=flavor_id,
                                                           image_id=image_id,
                                                           project_id=project_id,
                                                           networks=[], personality=[])
        except ClientError as ex:
            raise ex
        return okeanos_response

    def create_vpn(self, network_name):
        """
        Creates a virtual private network
        :param network_name: name of the network
        :return: the id of the network if successfull
        """
        try:
            # Create vpn with custom type and the name given as argument
            vpn = self.network_client.create_network(
                        type=self.network_client.network_types[1],
                        name=network_name)
            return vpn['id']
        except ClientError as ex:
            raise ex
        return okeanos_response

    def destroy_vpn(self, id):
        """
        Destroy a virtual private network
        :param id: id of the network we want to destroy
        :return: True if successfull
        """
        try:
            self.network_client.delete_network(id)
            return True
        except ClientError as ex:
            raise ex
        return okeanos_response

    def reserve_ip(self):
        """
        Reserve ip
        :return: the ip object if successfull
        """
        try:
            ip = self.network_client.create_floatingip()
            return ip
        except ClientError as ex:
            raise ex
        return okeanos_response

    def create_private_subnet(self, net_id):
        """
        Creates a private subnets and connects it with this network
        :param net_id: id of the network
        :return: the id of the subnet if successfull
        """
        cidr = "192.168.0.0/24"
        gateway_ip = "192.168.0.1"
        try:
            subnet = self.network_client.create_subnet(net_id, cidr,
                                                       gateway_ip=gateway_ip,
                                                       enable_dhcp=True)
            return subnet['id']
        except ClientError as ex:
            raise ex
        return okeanos_response

    def connect_vm(self, vm_id, net_id):
        """
        Connects the vm with this id to the network with the net_id
        :param vm_id: id of the vm
        :param net_id: id of the network
        :return: returns True if successfull
        """
        try:
            port = self.network_client.create_port(network_id=net_id,
                                                   device_id=vm_id)
            return True
        except ClientError as ex:
            raise ex
        return okeanos_response

    def attach_public_ip(self, ip, vm_id):
        """
        Attach the public ip with this id to the vm
        :param fnet_id: id of the floating network of the ip
        :param vm_id: id of the vm
        :return: returns True if successfull
        """
        try:
            port = self.network_client.create_port(network_id=ip['floating_network_id'],
                                                   device_id=vm_id,
                                                   fixed_ips=[dict(ip_address=ip['floating_ip_address']), ])
            return True
        except ClientError as ex:
            raise ex
        return okeanos_response

    def get_quotas(self, **kwargs):
        """
        Get the user quotas for the defined project.
        :return: user quotas object
        """
        return self.identity_client.get_quotas()

    def check_cluster_size_quotas(self, quotas, project_id, cluster_size):
        """
        Checks if the user quota is enough to create the requested number
        of VMs.
        :param quotas: quotas object retrieved by the AstakosClient.
        :param project_id: id of the project.
        :param cluster_size: number of VMs we request.
        :return:True if there are enough VMs for that request.
        """
        pending_vm = quotas[project_id]['cyclades.vm']['pending']
        limit_vm = quotas[project_id]['cyclades.vm']['limit']
        usage_vm = quotas[project_id]['cyclades.vm']['usage']
        available_vm = limit_vm - usage_vm - pending_vm
        if available_vm < cluster_size:
            msg = 'Cyclades VMs out of limit'
            raise ClientError(msg, error_quotas_cluster_size)
        else:
            return True

    def check_cpu_quotas(self, quotas, project_id, cpu_request):
        """
        Checks if the user quota is enough to create the requested number
        of VMs.
        :param quotas: quotas object retrieved by the AstakosClient.
        :param project_id: id of the project.
        :param cpu_request: number of CPUs we request.
        :return:True if there are enough CPUs for that request.
        """
        pending_cpu = quotas[project_id]['cyclades.cpu']['pending']
        limit_cpu = quotas[project_id]['cyclades.cpu']['limit']
        usage_cpu = quotas[project_id]['cyclades.cpu']['usage']
        available_cpu = limit_cpu - usage_cpu - pending_cpu
        if available_cpu < cpu_request:
            msg = 'Cyclades cpu out of limit'
            raise ClientError(msg, error_quotas_cpu)
        else:
            return True

    def check_ram_quotas(self, quotas, project_id, ram_request):
        """
        Checks if the user quota is enough to bind the requested ram resources.
        Subtracts the number of ram used and pending from the max allowed
        number of ram.
        :param quotas: quotas object retrieved by the AstakosClient.
        :param project_id: id of the project.
        :param ram_request: amount of RAM we request in MBs.
        :return:True if there is enough available RAM for that request.
        """
        pending_ram = quotas[project_id]['cyclades.ram']['pending']
        limit_ram = quotas[project_id]['cyclades.ram']['limit']
        usage_ram = quotas[project_id]['cyclades.ram']['usage']
        available_ram = (limit_ram - usage_ram - pending_ram) / self.Bytes_to_MB
        if available_ram < ram_request:
            msg = 'Cyclades ram out of limit'
            raise ClientError(msg, error_quotas_ram)
        else:
            return True

    def check_disk_quotas(self, quotas, project_id, disk_request):
        """
        Checks if the requested disk resources are available for the user.
        Subtracts the number of disk used and pending from the max allowed
        disk size.
        :param quotas: quotas object retrieved by the AstakosClient.
        :param project_id: id of the project.
        :param disk_request: amount of Disk space we request in GBs.
        :return:True if there is enough available Disk space for that request.
        """
        pending_cd = quotas[project_id]['cyclades.ram']['pending']
        limit_cd = quotas[project_id]['cyclades.disk']['limit']
        usage_cd = quotas[project_id]['cyclades.disk']['usage']
        available_cyclades_disk_GB = (limit_cd - usage_cd - pending_cd) / self.Bytes_to_GB
        if available_cyclades_disk_GB < disk_request:
            msg = 'Cyclades disk out of limit'
            raise ClientError(msg, error_quotas_cyclades_disk)
        else:
            return True

    def check_ip_quotas(self, quotas, project_id, ip_request):
        """Checks user's quota for unattached public ips.
        :param quotas: quotas object retrieved by the AstakosClient.
        :param project_id: id of the project.
        :param ip_request: number of public ips we request.
        :return:True if there are enough public ips for that request.
        """
        list_float_ips = self.network_client.list_floatingips()
        pending_ips = quotas[project_id]['cyclades.floating_ip']['pending']
        limit_ips = quotas[project_id]['cyclades.floating_ip']['limit']
        usage_ips = quotas[project_id]['cyclades.floating_ip']['usage']

        available_ips = limit_ips - usage_ips - pending_ips
        for d in list_float_ips:
            if d['instance_id'] is None and d['port_id'] is None:
                available_ips += 1
        if available_ips < ip_request:
            msg = 'Public IPs out of limit'
            raise ClientError(msg, error_quotas_cyclades_disk)
        else:
            return True

    def check_network_quotas(self, quotas, project_id, network_request):
        """
        Checks if the user quota is enough to create a new private network
        Subtracts the number of networks used and pending from the max allowed
        number of networks
        """
        pending_net = quotas[project_id]['cyclades.network.private']['pending']
        limit_net = quotas[project_id]['cyclades.network.private']['limit']
        usage_net = quotas[project_id]['cyclades.network.private']['usage']
        available_networks = limit_net - usage_net - pending_net
        if available_networks < 1:
            msg = 'Private Network out of limit'
            raise ClientError(msg, error_quotas_cyclades_disk)
        else:
            return True

    def check_all_resources(self, **kwargs):
        """
        Checks user's quota for every requested resource.
        Returns True if everything available.
        :param **kwargs: arguments
        """
        project_id = self.find_project_id(**kwargs)['id']
        quotas = self.get_quotas()
        # Check for VMs
        try:
            self.check_cluster_size_quotas(quotas, project_id, kwargs.get("cluster_size"))
        except ClientError as ex:
            raise ex
            return False
        # Check for CPUs
        try:
            self.check_cpu_quotas(quotas, project_id, kwargs.get("cpu_request"))
        except ClientError as ex:
            raise ex
            return False
        # Check for RAM
        try:
            self.check_ram_quotas(quotas, project_id, kwargs.get("ram_request"))
        except ClientError as ex:
            raise ex
            return False
        # Check for Disk space
        try:
            self.check_disk_quotas(quotas, project_id, kwargs.get("disk_request"))
        except ClientError as ex:
            raise ex
            return False
        # Check for public IPs
        try:
            self.check_ip_quotas(quotas, project_id, kwargs.get("ip_request"))
        except ClientError as ex:
            raise ex
            return False
        # Check for networks
        try:
            self.check_network_quotas(quotas, project_id, kwargs.get("network_request"))
        except ClientError as ex:
            raise ex
            return False
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Okeanos VM provisioning")
    parser.add_argument('--cloud', type=str, dest="cloud", default="~okeanos")
    parser.add_argument('--project-name', type=str, dest="project_name",
                        default="lambda.grnet.gr")
    parser.add_argument('--name', type=str, dest='name', default="to mikro debian sto livadi")

    parser.add_argument('--cluster_size', type=int, dest='cluster_size', default=3)
    parser.add_argument('--cpu_request', type=int, dest='cpu_request', default=3)
    parser.add_argument('--ram_request', type=int, dest='ram_request', default=4000)  # in MB
    parser.add_argument('--disk_request', type=int, dest='disk_request', default=400)  # in GB
    parser.add_argument('--ip_request', type=int, dest='ip_request', default=1)
    parser.add_argument('--network_request', type=int, dest='network_request', default=1)

    args = parser.parse_args()

    # Run Provisioner methods
    provisioner = Provisioner(cloud_name=args.cloud)
    print(provisioner.check_all_resources(cluster_size=args.cluster_size,
                                          cpu_request=args.cpu_request,
                                          ram_request=args.ram_request,
                                          disk_request=args.disk_request,
                                          ip_request=args.ip_request,
                                          network_request=args.network_request,
                                          project_name=args.project_name))
    # provisioner.get_quotas(project_name=args.project_name)
    # provisioner.create_vm(vm_name=args.name, project_name=args.project_name, image_name="debian")
    # provisioner.create_vm(vm_name="to mikro ubuntu sto livadi", project_name=args.project_name)
    # net_id = provisioner.create_vpn("test")
    # print provisioner.create_private_subnet(net_id)
    # provisioner.connect_vm(663972,net_id)
    # ip =  provisioner.reserve_ip()
    # print ip['id']
    # provisioner.attach_public_ip(ip,663972)
    # provisioner.attach_vm_to_network(663972,net_id)
