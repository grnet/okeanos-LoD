#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from __future__ import __all__

from kamaki.clients import ClientError
from kamaki.clients.utils import https
from kamaki.cli.config import Config as KamakiConfig

# TODO: remove this and actually use ssl cert files
https.patch_ignore_ssl()

import argparse

from kamaki.clients import astakos, cyclades


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
        :return: the id of the network if it was successfully created,
        else returns False
        """

        #create vpn with custom type and the name given as argument
        vpn = self.network_client.create_network(
            type=self.network_client.network_types[1],
            name=network_name)
        if vpn != None:
            return vpn['id']
        return False

    def destroy_vpn(self, id):
        """
        Destroy a virtual private network
        :param id: id of the network we want to destroy
        """
        self.network_client.delete_network(id)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Okeanos VM provisioning")
    parser.add_argument('--cloud', type=str, dest="cloud", default="lambda")
    parser.add_argument('--project-name', type=str, dest="project_name", default="lambda.grnet.gr")

    args = parser.parse_args()
    provisioner = Provisioner(cloud_name="~okeanos", project_name=args.project_name)

    #run provisioner methods
    #provisioner.create_vm(vm_name="to mikro ubuntu sto livadi", project_name=args.project_name)
    net_id = provisioner.create_vpn("test")
    provisioner.destroy_vpn(net_id)
