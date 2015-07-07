import mock

from fokia.provisioner import Provisioner

import sys as s
print "Package six in packages == ", 'six' in s.modules.keys()

def test_find_flavor(monkeypatch):
    with mock.patch('kamaki.clients.astakos'):
        provisioner = Provisioner("lambda")

    assert "C1R1024D40drbd" == provisioner.find_flavor()['name']
