from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from kamaki.clients import astakos, cyclades
from kamaki.clients import ClientError
from kamaki.cli.config import Config as KamakiConfig
from fokia.utils import patch_certs
from fokia.cluster_error_constants import *
from Crypto.PublicKey import RSA
from base64 import b64encode

from fokia.provisioner_base import ProvisionerBase

storage_templates = ['drdb', 'ext_vlmc']


class Provisioner(ProvisionerBase):
    """
        provisions virtual machines on ~okeanos
    """

    def __init__(self, auth_token, cloud_name=None):
        super(Provisioner, self).__init__(auth_token=auth_token, cloud_name=cloud_name)
        self.master = None
        self.slaves = None
        self.vms = [self.master, self.slaves]

    """
    CREATE RESOURCES
    """

    def create_lambda_cluster(self, vm_name, wait=True, **kwargs):
        """
        :param vm_name: hostname of the master
        :param kwargs: contains specifications of the vms.
        :return: dictionary object with the nodes of the cluster if it was successfully created
        """
        quotas = self.get_quotas()
        vcpus = kwargs['slaves'] * kwargs['vcpus_slave'] + kwargs['vcpus_master']
        ram = kwargs['slaves'] * kwargs['ram_slave'] + kwargs['ram_master']
        disk = kwargs['slaves'] * kwargs['disk_slave'] + kwargs['disk_master']
        project_id = self.find_project_id(**kwargs)['id']
        cluster_size = kwargs['slaves'] + 1
        extra_pub_keys = kwargs.get('extra_pub_keys') or []
        if not hasattr(extra_pub_keys, '__iter__'):
            extra_pub_keys = [extra_pub_keys]
        response = self.check_all_resources(quotas, cluster_size=cluster_size,
                                            vcpus=vcpus,
                                            ram=ram,
                                            disk=disk,
                                            ip_allocation=kwargs['ip_allocation'],
                                            network_request=kwargs['network_request'],
                                            project_name=kwargs['project_name'])

        if response:
            # Check flavors for master and slaves
            master_flavor = self.find_flavor(vcpus=kwargs['vcpus_master'],
                                             ram=kwargs['ram_master'],
                                             disk=kwargs['disk_master'])
            if not master_flavor:
                msg = 'This flavor does not allow create.'
                raise ClientError(msg, error_flavor_list)

            slave_flavor = self.find_flavor(vcpus=kwargs['vcpus_slave'],
                                            ram=kwargs['ram_slave'],
                                            disk=kwargs['disk_slave'])
            if not slave_flavor:
                msg = 'This flavor does not allow create.'
                raise ClientError(msg, error_flavor_list)

            # Get ssh keys
            key = RSA.generate(2048)
            self.private_key = key.exportKey('PEM')
            pub_key = key.publickey().exportKey('OpenSSH') + ' root'
            extra_pub_keys.append(pub_key)
            pub_keys = '\n'.join(extra_pub_keys)
            public = dict(contents=b64encode(pub_key),
                          path='/root/.ssh/id_rsa.pub',
                          owner='root', group='root', mode=0600)
            authorized = dict(contents=b64encode(pub_keys),
                              path='/root/.ssh/authorized_keys',
                              owner='root', group='root', mode=0600)
            private = dict(contents=b64encode(self.private_key),
                           path='/root/.ssh/id_rsa',
                           owner='root', group='root', mode=0600)

            master_personality = [authorized, public, private]
            slave_personality = [authorized]

            # Create private network for cluster
            self.vpn = self.create_vpn('lambda-vpn', project_id=project_id)
            vpn_id = self.vpn['id']
            self.create_private_subnet(vpn_id)

            master_ip = None
            slave_ips = [None] * kwargs['slaves']
            # reserve ip
            if kwargs['ip_allocation'] in ["master", "all"]:
                master_ip = self.reserve_ip(project_id=project_id)

                if kwargs['ip_allocation'] == "all":
                    slave_ips = [self.reserve_ip(project_id=project_id)
                                 for i in range(kwargs['slaves'])]

            self.ips = [ip for ip in [master_ip] + slave_ips if ip]

            self.master = self.create_vm(vm_name=vm_name, ip=master_ip,
                                         net_id=vpn_id,
                                         flavor=master_flavor,
                                         personality=master_personality,
                                         **kwargs)

            # Create slaves
            self.slaves = list()
            for i in range(kwargs['slaves']):
                slave_name = 'lambda-node' + str(i + 1)
                slave = self.create_vm(vm_name=slave_name,
                                       ip=slave_ips[i],
                                       net_id=vpn_id,
                                       flavor=slave_flavor,
                                       personality=slave_personality,
                                       **kwargs)
                self.slaves.append(slave)

            # Wait for VMs to complete being built
            if wait:
                self.cyclades.wait_server(server_id=self.master['id'])
                for slave in self.slaves:
                    self.cyclades.wait_server(slave['id'])

            # Create cluster dictionary object
            inventory = {
                "master": self.master,
                "slaves": self.slaves
            }
            return inventory

    """
    DELETE RESOURCES
    """

    def delete_lambda_cluster(self, details):
        """
        Delete a lambda cluster
        :param details: details of the cluster we want to delete
        :return: True if successfull
        """

        # Delete every node
        nodes = details['nodes']
        for node in nodes:
            if (not self.delete_vm(node)):
                msg = 'Error deleting node with id ', node
                raise ClientError(msg, error_fatal)

        # Wait to complete deleting VMs
        for node in nodes:
            self.cyclades.wait_server(server_id=node, current_status='ACTIVE')

        # Delete vpn
        vpn = details['vpn']
        if (not self.delete_vpn(vpn)):
            msg = 'Error deleting node with id ', node
            raise ClientError(msg, error_fatal)

    """
    GET RESOURCES
    """

    def get_cluster_details(self):
        """
        :returns: dictionary of basic details for the cluster
        """
        details = dict()

        nodes = dict()
        master = dict()
        master['id'] = self.master['id']
        master['name'] = self.master['name']
        master['adminPass'] = self.master['adminPass']
        nodes['master'] = master

        slaves = list()
        for slave in self.slaves:
            slave_obj = dict()
            slave_obj['id'] = slave['id']
            slave_obj['name'] = slave['name']
            name = slave_obj['name']
            slaves.append(slave_obj)
        nodes['slaves'] = slaves

        details['nodes'] = nodes
        vpn = dict()
        vpn['id'] = self.vpn['id']
        vpn['type'] = self.vpn['type']
        details['vpn'] = vpn

        details['ips'] = self.ips
        ips_list = list()
        for ip in self.ips:
            ip_obj = dict()
            ip_obj['floating_network_id'] = ip['floating_network_id']
            ip_obj['floating_ip_address'] = ip['floating_ip_address']
            ip_obj['id'] = ip['id']
            ips_list.append(ip_obj)
        details['ips'] = ips_list

        subnet = dict()
        subnet['id'] = self.subnet['id']
        subnet['cidr'] = self.subnet['cidr']
        subnet['gateway_ip'] = self.subnet['gateway_ip']
        details['subnet'] = subnet
        return details

    """
    CHECK RESOURCES
    """

    def check_all_resources(self, quotas, **kwargs):
        """
        Checks user's quota for every requested resource.
        Returns True if everything available.
        :param **kwargs: arguments
        """
        project_id = self.find_project_id(**kwargs)['id']
        # Check for VMs
        pending_vm = quotas[project_id]['cyclades.vm']['project_pending']
        limit_vm = quotas[project_id]['cyclades.vm']['project_limit']
        usage_vm = quotas[project_id]['cyclades.vm']['project_usage']
        available_vm = limit_vm - usage_vm - pending_vm
        if available_vm < kwargs['cluster_size']:
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
        list_float_ips = self.network_client.list_floatingips()
        pending_ips = quotas[project_id]['cyclades.floating_ip']['project_pending']
        limit_ips = quotas[project_id]['cyclades.floating_ip']['project_limit']
        usage_ips = quotas[project_id]['cyclades.floating_ip']['project_usage']
        available_ips = limit_ips - usage_ips - pending_ips
        # TODO: figure out how to handle unassigned floating ips
        # for d in list_float_ips:
        #     if d['instance_id'] is None and d['port_id'] is None:
        #         available_ips += 1
        if (kwargs['ip_allocation'] == "master" and available_ips < 1) or \
                (kwargs['ip_allocation'] == "all" and available_ips < kwargs['cluster_size']):
            msg = 'authorized IPs out of limit'
            raise ClientError(msg, error_get_ip)
        # Check for networks
        pending_net = quotas[project_id]['cyclades.network.private']['project_pending']
        limit_net = quotas[project_id]['cyclades.network.private']['project_limit']
        usage_net = quotas[project_id]['cyclades.network.private']['project_usage']
        available_networks = limit_net - usage_net - pending_net
        if available_networks < kwargs['network_request']:
            msg = 'Private Network out of limit'
            raise ClientError(msg, error_get_network_quota)
        return True
