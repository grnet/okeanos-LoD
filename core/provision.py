from os.path import join, expanduser
from ConfigParser import ConfigParser

from kamaki.clients import ClientError
from kamaki.clients.utils import https
from kamaki.cli.config import Config as KamakiConfig

https.patch_ignore_ssl()

import argparse

from kamaki.clients import astakos, cyclades


def parse_kamakirc(filepath=None):
    """
    Parse the kamaki configuration
    """
    parser = ConfigParser()

    # Default to ~/.kamakirc if filepath is not given
    if filepath == None:
        filepath = join(expanduser('~'), ".kamakirc")
    parser.read(filepath)

    return parser


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

    def find_flavor(self, vcpus=1, ram=1024, disk=40, **kwargs):
        """

        :param vcpus: Number of cpus
        :param ram: Amount of ram megabytes
        :param disk:  Amount of disk gigabytes
        :param kwargs:
        :return: first flavor objects that matches the criteria
        """
        for flavor in self.cyclades.list_flavors(detail=True):
            if flavor['ram'] == ram and flavor['vcpus'] == vcpus and flavor['disk'] == disk:
                return flavor
        return None

    def find_image(self, image_name="debian", version="", **kwargs):
        for image in self.cyclades.list_images(detail=True):
            if image_name in image['name'] and version in image['name']:
                return image
        return None

    def find_project_id(self, **kwargs):
        filter = {
            'name': kwargs.get("project_name")
        }
        return self.astakos.get_projects(**filter)[0]

    def create_vm(self, vm_name=None, **kwargs):
        flavor_id = self.find_flavor(**kwargs)['id']
        image_id = self.find_image(**kwargs)['id']
        project_id = self.find_project_id(**kwargs)['id']
        try:
            print self.cyclades.create_server(name=vm_name, flavor_id=flavor_id,
                                              image_id=image_id, project_id=project_id,
                                              networks=[])
        except ClientError as ex:
            print ex



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Okeanos VM provisioning")
    parser.add_argument('--cloud', type=str, dest="cloud", default="lambda")
    parser.add_argument('--project-name', type=str, dest="project_name", default="lambda.grnet.gr")

    args = parser.parse_args()
    provisioner = Provisioner(cloud_name=args.cloud, project_name=args.project_name)
    provisioner.create_vm(vm_name="to mikro ubuntu sto livadi", project_name=args.project_name)
