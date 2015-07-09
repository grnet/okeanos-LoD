# -*- coding: utf-8 -*-

""" Functionality related to unit tests with un-managed resources mocked. """
# setup testing framework
from unittest import TestCase, main, expectedFailure, skip
from mock import patch
import sys
import os
from os.path import join, dirname, abspath
from mock import patch
from ConfigParser import RawConfigParser, NoSectionError


sys.path.append(join(dirname(abspath(__file__)), '../'))

# import objects we aim to test
import provision
import cluster_error_constants


class MockAstakos():
    """ support class for faking AstakosClient.get_quotas """

    def get_quotas(self, *args):
        return { 'test_project_id':
                     {'cyclades.disk':
                          {'project_limit': 1288490188800, 'project_pending': 0, 'project_usage': 64424509440, 'usage': 0, 'limit': 322122547200, 'pending': 0},
                      'cyclades.vm':
                          {'project_limit': 60, 'project_pending': 0, 'project_usage': 2, 'usage': 0, 'limit': 15, 'pending': 0},
                      'pithos.diskspace':
                          {'project_limit': 429496729600, 'project_pending': 0, 'project_usage': 0, 'usage': 0, 'limit': 107374182400, 'pending': 0},
                      'cyclades.ram':
                          {'project_limit': 128849018880, 'project_pending': 0, 'project_usage': 12884901888, 'usage': 0, 'limit': 32212254720, 'pending': 0},
                      'cyclades.cpu':
                          {'project_limit': 120, 'project_pending': 0, 'project_usage': 12, 'usage': 0, 'limit': 30, 'pending': 0},
                      'cyclades.floating_ip':
                          {'project_limit': 10, 'project_pending': 0, 'project_usage': 6, 'usage': 3, 'limit': 4, 'pending': 0},
                      'cyclades.network.private':
                          {'project_limit': 10, 'project_pending': 0, 'project_usage': 7, 'usage': 0, 'limit': 4, 'pending': 0},
                      'astakos.pending_app':
                          {'project_limit': 0, 'project_pending': 0, 'project_usage': 0, 'usage': 0, 'limit': 0, 'pending': 0}} }

class MockCycladesNetClient():
    """ support class for faking CycladesNetworkClient.list_floatingips """

    def list_floatingips(self):
        return [{'instance_id': '604863', 'port_id': '1743733'}, {'instance_id': None, 'port_id': None},
                {'instance_id': '615302', 'port_id': '1773954'}]

# replace unmanaged calls with fakes
@patch('provision.Cluster.create_vpn', mock_create_vpn)
class TestCreateCluster(TestCase):
    """ Test cases with separate un-managed resources mocked. """
    # initialize objects common to all tests in this test case#
    def setUp(self):
        cloud_name = '~okeanos'
        self.provisioner = provision.Provisioner(cloud_name=cloud_name)
        self.astakos = MockAstakos()
        self.quotas = self.astakos.get_quotas()
        self.opts = {
            'name': 'Test', 'cluster_size': 2, 'cpu_master': 2, 'cluster_size_ex': 100, 'cpu_master_ex': 100,
            'ram_master': 4096, 'disk_master': 5, 'cpu_slaves': 2, 'cpu_slaves_ex': 100, 'disk_master_ex': 10000,
            'ram_slaves': 2048, 'disk_slaves': 5, 'disk_slaves_ex': 10000, 'token': self.provisioner.auth_token,
            'ram_master_ex': 100000, 'ram_slaves_ex': 100000,
            'cluster_size_ex': 1000,
            'vpn': 1, 'vpn_ex': 20, 'ips': 1, 'ips_ex': 100,
            'os_choice': 'debian',
            'auth_url': self.provisioner.auth_url,
            'cloud_name':cloud_name,
            'project_id': 'test_project_id',
            'project_name': 'test_project'}

    """ Test Resource Checking methods """
    def test_check_vm_quotas_sufficient(self):
        # arrange
        expected = True  # success
        # act
        returned = self.provisioner.check_cluster_size_quotas(self.quotas, self.opts['project_id'], self.opts['cluster_size'])
        # assert
        self.assertEqual(expected, returned)

    def test_check_vm_quotas_exceeds(self):
        # arrange
        expected = False  # success
        # act
        returned = self.provisioner.check_cluster_size_quotas(self.quotas, self.opts['project_id'], self.opts['cluster_size_ex'])
        # assert
        self.assertEqual(expected, returned)

    def test_check_cpu_quotas_sufficient(self):
        # arrange
        cpus = self.opts['cpu_master'] + self.opts['cpu_slaves']
        expected = True  # success
        # act
        returned = self.provisioner.check_cpu_quotas(self.quotas, self.opts['project_id'], cpus)
        # assert
        self.assertEqual(expected, returned)

    def test_check_cpu_quotas_exceeds(self):
        # arrange
        cpus = self.opts['cpu_master_ex'] + self.opts['cpu_slaves_ex']
        expected = False  # success
        # act
        returned = self.provisioner.check_cpu_quotas(self.quotas, self.opts['project_id'], cpus)
        # assert
        self.assertEqual(expected, returned)

    def test_check_ram_quotas_sufficient(self):
        # arrange
        ram = self.opts['ram_master'] + self.opts['ram_slaves']
        expected = True  # success
        # act
        returned = self.provisioner.check_ram_quotas(self.quotas, self.opts['project_id'], ram)
        # assert
        self.assertEqual(expected, returned)

    def test_check_ram_quotas_exceeds(self):
        # arrange
        ram = self.opts['ram_master_ex'] + self.opts['ram_slaves_ex']
        expected = False  # success
        # act
        returned = self.provisioner.check_ram_quotas(self.quotas, self.opts['project_id'], ram)
        # assert
        self.assertEqual(expected, returned)

    def test_check_disk_quotas_sufficient(self):
        # arrange
        disk = self.opts['disk_master'] + self.opts['disk_slaves']
        expected = True  # success
        # act
        returned = self.provisioner.check_disk_quotas(self.quotas, self.opts['project_id'], disk)
        # assert
        self.assertEqual(expected, returned)

    def test_check_disk_quotas_exceeds(self):
        # arrange
        disk = self.opts['disk_master_ex'] + self.opts['disk_slaves_ex']
        expected = False  # success
        # act
        returned = self.provisioner.check_disk_quotas(self.quotas, self.opts['project_id'], disk)
        # assert
        self.assertEqual(expected, returned)

    def test_check_ip_quotas_sufficient(self):
        # arrange
        expected = True  # success
        # act
        returned = self.provisioner.check_ip_quotas(self.quotas, self.opts['project_id'], self.opts['ips'])
        # assert
        self.assertEqual(expected, returned)

    def test_check_ip_quotas_exceeds(self):
        # arrange
        expected = False  # success
        # act
        returned = self.provisioner.check_ip_quotas(self.quotas, self.opts['project_id'], self.opts['ips_ex'])
        # assert
        self.assertEqual(expected, returned)

    def test_check_network_quotas_sufficient(self):
        # arrange
        expected = True  # success
        # act
        returned = self.provisioner.check_network_quotas(self.quotas, self.opts['project_id'], self.opts['vpn'])
        # assert
        self.assertEqual(expected, returned)

    def test_check_network_quotas_exceeds(self):
        # arrange
        expected = False  # success
        # act
        returned = self.provisioner.check_network_quotas(self.quotas, self.opts['project_id'], self.opts['vpn_ex'])
        # assert
        self.assertEqual(expected, returned)

if __name__ == '__main__':
    main()
