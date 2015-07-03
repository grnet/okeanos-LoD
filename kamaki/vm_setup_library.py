#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from __future__ import __all__

from kamaki.clients import ClientError
from kamaki.clients.utils import https
from kamaki.cli.config import Config as KamakiConfig
from kamaki.clients import astakos, cyclades
import argparse

# TODO: remove this and actually use ssl cert files
https.patch_ignore_ssl()


class Provisioner:
    """
        Provisioner is responsible to provision virtual machines for a specified
        okeanos team
    """

    def __init__(self, cloud_name, project_name):

        self.project_name = project_name

        # Load .kamakirc configuration
        self.config = KamakiConfig()
        cloud_section = self.config._sections['cloud'][cloud_name]

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

    def find_flavor(self, vcpus=1, ram=1024, disk=40, **kwargs):
        """

        :param vcpus: Number of cpus
        :param ram: Amount of ram megabytes
        :param disk:  Amount of disk gigabytes
        :param kwargs:
        :return: first flavor objects that matches the specs criteria
        """
        for flavor in self.cyclades.list_flavors(detail=True):
            if flavor['ram'] == ram and flavor['vcpus'] == vcpus and flavor['disk'] == disk:
                return flavor
        return None

    def find_image(self, image_name="debian", **kwargs):
        """
        :param image_name: Name of the image to filter by
        :param kwargs:
        :return: first image object that matches the name criteria
        """
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
                                                           image_id=image_id, project_id=project_id,
                                                           networks=[])
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
        :return: the id of the ip if successfull
        """
        try:
            ip = self.network_client.create_floatingip()
            return ip['id']
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
                                                   device_id=vm_id,)
            return True
        except ClientError as ex:
            raise ex
        return okeanos_response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Okeanos VM provisioning")
    parser.add_argument('--cloud', type=str, dest="cloud", default="lambda")
    parser.add_argument('--project-name', type=str, dest="project_name", default="lambda.grnet.gr")

    args = parser.parse_args()
    provisioner = Provisioner(cloud_name="~okeanos", project_name=args.project_name)

    # run provisioner methods
    # provisioner.create_vm(vm_name="to mikro ubuntu sto livadi", project_name=args.project_name)
    # net_id = provisioner.create_vpn("test")
    # print provisioner.create_private_subnet(net_id)
    # provisioner.connect_vm(663972,net_id)
    # provisioner.reserve_ip()
    # provisioner.attach_vm_to_network(663972,net_id)
