from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from kamaki.clients import astakos, cyclades
from kamaki.clients import ClientError
from kamaki.clients.utils import https
from kamaki.cli.config import Config as KamakiConfig
from cluster_error_constants import *

# TODO: remove this and actually use ssl cert files
https.patch_ignore_ssl()

import argparse

storage_templates = ['drdb', 'ext_vlmc']


class Provisioner:
    """
        provisions virtual machines on ~okeanos
    """

    def __init__(self, cloud_name):

        # Load .kamakirc configuration
        logger.info("Retrieving .kamakirc configuration")
        self.config = KamakiConfig()
        cloud_section = self.config._sections['cloud'].get(cloud_name)
        if not cloud_section:
            message = "Cloud '%s' was not found in you .kamakirc configuration file. " \
                      "Currently you have availablie in your configuration these clouds: %s"
            raise KeyError(message % (cloud_name, self.config._sections['cloud'].keys()))

        # Get the authentication url and token
        auth_url, auth_token = cloud_section['url'], cloud_section['token']

        logger.info("Initiating Astakos Client")
        self.astakos = astakos.AstakosClient(auth_url, auth_token)

        logger.info("Retrieving cyclades endpoint url")
        compute_url = self.astakos.get_endpoint_url(
            cyclades.CycladesComputeClient.service_type)
        logger.info("Initiating Cyclades client")
        self.cyclades = cyclades.CycladesComputeClient(compute_url, auth_token)

        # Create the network client
        networkURL = self.astakos.get_endpoint_url(
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
        logger.info("Retrieving flavor")
        for flavor in self.cyclades.list_flavors(detail=True):
            if all([kwargs[key] == flavor[key] \
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

        logger.info("Retrieving image")
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
        logger.info("Retrieving project")
        return self.astakos.get_projects(**filter)[0]

    def create_vm(self, vm_name=None, ip=None, **kwargs):
        """
        :param vm_name: Name of the virtual machine to create
        :param kwargs: passed to the functions called for detail options
        :return:
        """
        flavor_id = self.find_flavor(**kwargs)['id']
        image_id = self.find_image(**kwargs)['id']
        project_id = self.find_project_id(**kwargs)['id']
        networks = [{'uuid': kwargs['net_id']}]
        if ip != None:
            ip_obj = dict()
            ip_obj['uuid'] = ip['floating_network_id']
            ip_obj['fixed_ip'] = ip['floating_ip_address']
            networks.append(ip_obj)
        try:
            okeanos_response = self.cyclades.create_server(name=vm_name, flavor_id=flavor_id,
                                                           image_id=image_id,
                                                           project_id=project_id,
                                                           networks=networks, personality=[])
        except ClientError as ex:
            raise ex
        return okeanos_response

    def create_lambda_cluster(self, vm_name, **kwargs):
        """
        :param vm_name: hostname of the master
        :param kwargs: contains specifications of the vms.
        """
        quotas = self.get_quotas()
        vcpus = kwargs['slaves'] * kwargs['vcpus_slave'] + kwargs['vcpus_master']
        ram = kwargs['slaves'] * kwargs['ram_slave'] + kwargs['ram_master']
        disk = kwargs['slaves'] * kwargs['disk_slave'] + kwargs['disk_master']
        response = self.check_all_resources(quotas, cluster_size=kwargs['cluster_size'],
                                              vcpus=vcpus,
                                              ram=ram,
                                              disk=disk,
                                              ip_request=kwargs['ip_request'],
                                              network_request=kwargs['network_request'],
                                              project_name=kwargs['project_name'])
        if response:

            # Create private network for cluster
            vpn_id = self.create_vpn('lambda-vpn')
            self.create_private_subnet(vpn_id)

            #reserve ip
            ip_request=kwargs['ip_request']
            ips = list()
            for i in range(ip_request-1):
                ip = self.reserve_ip()
                ips.append(ip)

            ip = None
            # Create master
            if len(ips) > 0:
                ip = ips[0]
            master = self.create_vm(vm_name=vm_name, ip=ip, net_id=vpn_id, vcpus=kwargs['vcpus_master'], ram=kwargs['ram_master'], disk=kwargs['disk_master'], **kwargs)

            # Create slaves
            slaves = list()
            for i in range(kwargs['slaves']):
                ip = None
                if len(ips) > i+2:
                    ip = ips[i+2]
                slave_name = 'lambda-node' + str(i+1)
                slave = self.create_vm(vm_name=slave_name, ip=ip, net_id=vpn_id, vcpus=kwargs['vcpus_slave'], ram=kwargs['ram_slave'], disk=kwargs['disk_slave'], **kwargs)
                slaves.append(slave)

            # Create cluster dictionary object
            inventory = dict()
            masters = list()
            masters.append(master)
            inventory["masters"] = masters
            inventory["slaves"] = slaves
            return inventory


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
        return self.astakos.get_quotas()

    def check_all_resources(self, quotas, **kwargs):
        """
        Checks user's quota for every requested resource.
        Returns True if everything available.
        :param **kwargs: arguments
        """
        project_id = self.find_project_id(**kwargs)['id']
        # quotas = self.get_quotas()

        # Check for VMs
        pending_vm = quotas[project_id]['cyclades.vm']['project_pending']
        limit_vm = quotas[project_id]['cyclades.vm']['project_limit']
        usage_vm = quotas[project_id]['cyclades.vm']['project_usage']
        available_vm = limit_vm - usage_vm - pending_vm
        if available_vm < kwargs['cluster_size']:
            msg = 'Cyclades VMs out of limit'
            raise ClientError(msg, error_quotas_cluster_size)
            return False
        # Check for CPUs
        pending_cpu = quotas[project_id]['cyclades.cpu']['project_pending']
        limit_cpu = quotas[project_id]['cyclades.cpu']['project_limit']
        usage_cpu = quotas[project_id]['cyclades.cpu']['project_usage']
        available_cpu = limit_cpu - usage_cpu - pending_cpu
        if available_cpu < kwargs['vcpus']:
            msg = 'Cyclades cpu out of limit'
            raise ClientError(msg, error_quotas_cpu)
            return False
        # Check for RAM
        pending_ram = quotas[project_id]['cyclades.ram']['project_pending']
        limit_ram = quotas[project_id]['cyclades.ram']['project_limit']
        usage_ram = quotas[project_id]['cyclades.ram']['project_usage']
        available_ram = (limit_ram - usage_ram - pending_ram) / self.Bytes_to_MB
        if available_ram < kwargs['ram']:
            msg = 'Cyclades ram out of limit'
            raise ClientError(msg, error_quotas_ram)
            return False
        # Check for Disk space
        pending_cd = quotas[project_id]['cyclades.ram']['project_pending']
        limit_cd = quotas[project_id]['cyclades.disk']['project_limit']
        usage_cd = quotas[project_id]['cyclades.disk']['project_usage']
        available_cyclades_disk_GB = (limit_cd - usage_cd - pending_cd) / self.Bytes_to_GB
        if available_cyclades_disk_GB < kwargs['disk']:
            msg = 'Cyclades disk out of limit'
            raise ClientError(msg, error_quotas_cyclades_disk)
            return False
        # Check for public IPs
        list_float_ips = self.network_client.list_floatingips()
        pending_ips = quotas[project_id]['cyclades.floating_ip']['project_pending']
        limit_ips = quotas[project_id]['cyclades.floating_ip']['project_limit']
        usage_ips = quotas[project_id]['cyclades.floating_ip']['project_usage']
        available_ips = limit_ips - usage_ips - pending_ips
        for d in list_float_ips:
            if d['instance_id'] is None and d['port_id'] is None:
                available_ips += 1
        if available_ips < kwargs['ip_request']:
            msg = 'Public IPs out of limit'
            raise ClientError(msg, error_get_ip)
            return False
        # Check for networks
        pending_net = quotas[project_id]['cyclades.network.private']['project_pending']
        limit_net = quotas[project_id]['cyclades.network.private']['project_limit']
        usage_net = quotas[project_id]['cyclades.network.private']['project_usage']
        available_networks = limit_net - usage_net - pending_net
        if available_networks < kwargs['network_request']:
            msg = 'Private Network out of limit'
            raise ClientError(msg, error_get_network_quota)
            return False
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Okeanos VM provisioning")
    parser.add_argument('--cloud', type=str, dest="cloud", default="~okeanos")
    parser.add_argument('--project-name', type=str, dest="project_name",
                        default="lambda.grnet.gr")
    parser.add_argument('--name', type=str, dest='name', default="to mikro debian sto livadi")


    parser.add_argument('--slaves', type=int, dest='slaves', default=1)
    parser.add_argument('--vcpus_master', type=int, dest='vcpus_master', default=4)
    parser.add_argument('--vcpus_slave', type=int, dest='vcpus_slave', default=4)
    parser.add_argument('--ram_master', type=int, dest='ram_master', default=4096)  # in MB
    parser.add_argument('--ram_slave', type=int, dest='ram_slave', default=4096)  # in MB
    parser.add_argument('--disk_master', type=int, dest='disk_master', default=40)  # in GB
    parser.add_argument('--disk_slave', type=int, dest='disk_slave', default=40)  # in GB
    parser.add_argument('--ip_request', type=int, dest='ip_request', default=1)
    parser.add_argument('--network_request', type=int, dest='network_request', default=1)
    parser.add_argument('--image_name', type=str, dest='image_name', default="debian")
    parser.add_argument('--cluster_size', type=int, dest='cluster_size', default=2)

    args = parser.parse_args()

    provisioner = Provisioner(cloud_name=args.cloud)
    """
    print(provisioner.create_vm(vm_name=args.name, project_name=args.project_name,
                             image_name="debian"))
    """


    provisioner.create_lambda_cluster(vm_name="lambda-master" , slaves=args.slaves,
                                          image_name=args.image_name,
                                          cluster_size=args.cluster_size,
                                          vcpus_master=args.vcpus_master,
                                          vcpus_slave=args.vcpus_slave,
                                          ram_master=args.ram_master,
                                          ram_slave=args.ram_slave,
                                          disk_master=args.disk_master,
                                          disk_slave=args.disk_slave,
                                          ip_request=args.ip_request,
                                          network_request=args.network_request,
                                          project_name=args.project_name)
