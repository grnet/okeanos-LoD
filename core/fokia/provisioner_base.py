from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from kamaki.clients import astakos, cyclades
from kamaki.clients import ClientError
from kamaki.cli.config import Config as KamakiConfig
from fokia.utils import patch_certs
from fokia.cluster_error_constants import *
from Crypto.PublicKey import RSA
from base64 import b64encode

import abc

storage_templates = ['drdb', 'ext_vlmc']

class ProvisionerBase:
    """
        provisions virtual machines on ~okeanos
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, auth_token, cloud_name=None):
        if auth_token is None:

            # Load .kamakirc configuration
            logger.info("Retrieving .kamakirc configuration")
            self.config = KamakiConfig()
            patch_certs(self.config.get('global', 'ca_certs'))
            if cloud_name is None:
                cloud_section = self.config._sections['cloud'].get(self.config.get('global', 'default_cloud'))
            else:
                cloud_section = self.config._sections['cloud'].get(cloud_name)
            if not cloud_section:
                message = "Cloud '%s' was not found in you .kamakirc configuration file. " \
                          "Currently you have available in your configuration these clouds: %s"
                raise KeyError(message % (cloud_name, self.config._sections['cloud'].keys()))

            # Get the authentication url and token
            auth_url, auth_token = cloud_section['url'], cloud_section['token']

        else:
            auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"

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
        self.Bytes_to_GB = 1024 * 1024 * 1024
        self.Bytes_to_MB = 1024 * 1024

        self.vms = []
        self.ips = None
        self.vpn = None
        self.subnet = None
        self.private_key = None
        self.image_id = 'c6f5adce-21ad-4ce3-8591-acfe7eb73c02'

    """
    FIND RESOURCES
    """

    def find_flavor(self, **kwargs):
        """

        :param kwargs: should contains the keys that specify the specs
        :return: first flavor objects that matches the specs criteria
        """

        # Set all the default parameters
        kwargs.setdefault("vcpus", 1)
        kwargs.setdefault("ram", 1024)
        kwargs.setdefault("disk", 40)
        kwargs.setdefault("SNF:allow_create", True)
        logger.info("Retrieving flavor")
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
            'name':  kwargs.get("project_name"),
            'state': kwargs.get("project_state"),
            'owner': kwargs.get("project_owner"),
            'mode':  kwargs.get("project_mode"),
        }
        logger.info("Retrieving project")
        return self.astakos.get_projects(**filter)[0]

    """
    CREATE RESOURCES
    """

    def create_vm(self, vm_name=None, image_id=None,
                  ip=None, personality=None, flavor=None, **kwargs):
        """
        :param vm_name: Name of the virtual machine to create
        :param image_id: image id if you want another image than the default
        :param kwargs: passed to the functions called for detail options
        :return:
        """
        flavor_id = flavor['id']
        # Get image
        if image_id == None:
            image_id = self.image_id
        else:
            image_id = self.find_image(**kwargs)['id']
        project_id = self.find_project_id(**kwargs)['id']
        networks = list()
        if ip:
            ip_obj = dict()
            ip_obj['uuid'] = ip['floating_network_id']
            ip_obj['fixed_ip'] = ip['floating_ip_address']
            networks.append(ip_obj)
        networks.append({'uuid': kwargs['net_id']})
        if personality == None:
            personality = []
        try:
            okeanos_response = self.cyclades.create_server(name=vm_name,
                                                           flavor_id=flavor_id,
                                                           image_id=image_id,
                                                           project_id=project_id,
                                                           networks=networks,
                                                           personality=personality)
        except ClientError as ex:
            raise ex
        return okeanos_response

    def create_vpn(self, network_name, project_id):
        """
        Creates a virtual private network
        :param network_name: name of the network
        :return: the virtual network object
        """
        try:
            # Create vpn with custom type and the name given as argument
            vpn = self.network_client.create_network(
                type=self.network_client.network_types[1],
                name=network_name,
                project_id=project_id)
            return vpn
        except ClientError as ex:
            raise ex

    def reserve_ip(self, project_id):
        """
        Reserve ip
        :return: the ip object if successfull
        """
        # list_float_ips = self.network_client.list_floatingips()
        # for ip in list_float_ips:
        #     if ip['instance_id'] is None and ip['port_id'] is None and ip not in ips:
        #         return ip
        try:
            ip = self.network_client.create_floatingip(project_id=project_id)
            return ip
        except ClientError as ex:
            raise ex

    def create_private_subnet(self, net_id, cidr='192.168.0.0/24', gateway_ip='192.168.0.1'):
        """
        Creates a private subnets and connects it with this network
        :param net_id: id of the network
        :return: the id of the subnet if successfull
        """
        try:
            subnet = self.network_client.create_subnet(net_id, cidr,
                                                       gateway_ip=gateway_ip,
                                                       enable_dhcp=True)
            self.subnet = subnet
            return subnet['id']
        except ClientError as ex:
            raise ex

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

    def attach_authorized_ip(self, ip, vm_id):
        """
        Attach the authorized ip with this id to the vm
        :param fnet_id: id of the floating network of the ip
        :param vm_id: id of the vm
        :return: returns True if successfull
        """
        try:
            port = self.network_client.create_port(network_id=ip['floating_network_id'],
                                                   device_id=vm_id,
                                                   fixed_ips=[dict(
                                                       ip_address=ip['floating_ip_address']), ])
            return True
        except ClientError as ex:
            raise ex

    """
    DELETE RESOURCES
    """

    def delete_vm(self, vm_id):
        """
        Delete a vm
        :param vm_id: id of the vm we want to delete
        :return: True if successfull
        """
        try:
            self.cyclades.delete_server(vm_id)
            return True
        except ClientError as ex:
            raise ex

    def delete_vpn(self, net_id):
        """
        Delete a virtual private network
        :param net_id: id of the network we want to delete
        :return: True if successfull
        """
        try:
            self.network_client.delete_network(net_id)
            return True
        except ClientError as ex:
            raise ex

    """
    GET RESOURCES
    """

    def get_private_key(self):
        """
        :returns: Private key of master
        """
        return self.private_key

    def get_quotas(self, **kwargs):
        """
        Get the user quotas for the defined project.
        :return: user quotas object
        """
        return self.astakos.get_quotas()

    def get_server_info(self, server_id):
        """
        """
        return self.cyclades.get_server_details(server_id=server_id)

    def get_server_authorized_ip(self, server_id):
        """
        :param server_id: id of the server
        :returns: the authorized ip of the server if it has one,else None
        """
        addresses = self.get_server_info(server_id=server_id)['addresses']
        for key in list(addresses.keys()):
            ip = addresses[key][0]['addr']
            if '192.168.0' not in ip and not re.search('[a-zA-Z]', ip):
                return ip
        return None

    def get_server_private_ip(self, server_id):
        """
        :param server_id: id of the server
        :returns: the private ip of the server if it has one,else None
        """
        addresses = self.get_server_info(server_id=server_id)['addresses']
        for key in list(addresses.keys()):
            ip = addresses[key][0]['addr']
            if '192.168.0' in ip:
                return ip
        return None

    """
    CHECK RESOURCES
    """

    @abc.abstractmethod
    def check_all_resources(self, quotas, **kwargs):
        """
        Checks user's quota for every requested resource.
        Returns True if everything available.
        :param **kwargs: arguments
        """
        return
