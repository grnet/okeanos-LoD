from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from kamaki.clients import astakos, cyclades
from kamaki.clients import ClientError
from kamaki.clients.utils import https
from kamaki.cli.config import Config as KamakiConfig

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Okeanos VM provisioning")
    parser.add_argument('--cloud', type=str, dest="cloud", default="lambda")
    parser.add_argument('--project-name', type=str, dest="project_name",
                        default="lambda.grnet.gr")
    parser.add_argument('--name', type=str, dest='name', default="to mikro debian sto livadi")

    args = parser.parse_args()

    provisioner = Provisioner(cloud_name=args.cloud)
    provisioner.create_vm(vm_name=args.name, project_name=args.project_name, image_name="debian")
