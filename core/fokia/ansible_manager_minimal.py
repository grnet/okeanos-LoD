import os
import ansible
from ansible.playbook import PlayBook
from ansible import callbacks
from ansible import utils


class Manager:
    def __init__(self, host, group, private_key_path=None):
        if private_key_path is None:
            private_key_path = os.path.expanduser('~/.ssh/id_rsa')
        ansible.constants.DEFAULT_TIMEOUT = 30
        ansible.constants.DEFAULT_PRIVATE_KEY_FILE = private_key_path
        ansible.constants.HOST_KEY_CHECKING = False

        self.ansible_inventory = ansible.inventory.Inventory(host_list=[host])
        all_group = self.ansible_inventory.get_group('all')
        ansible_host = all_group.get_hosts()[0]
        ansible_group = ansible.inventory.group.Group(name=group)
        ansible_group.add_host(ansible_host)
        self.ansible_inventory.add_group(ansible_group)
        all_group.add_child_group(ansible_group)

    def run_playbook(self, playbook_file, tags=None):
        """
        Run the playbook_file using created inventory and tags specified
        :return:
        """
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
        pb = PlayBook(playbook=playbook_file, inventory=self.ansible_inventory, stats=stats,
                      callbacks=playbook_cb,
                      runner_callbacks=runner_cb, only_tags=tags)
        playbook_result = pb.run()
        return playbook_result
