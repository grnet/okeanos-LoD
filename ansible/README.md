# Package and variable setup

## VM package and variable setup

Contains Ansible playbook for the installation of required packages and variables. The play is split into five (3) tasks:
- install packages and run basic commands on newly created vms.
- fetch public ssh key from master.
- distribute public key to all slave nodes.
Currently, the playbooks are run from an external node, and deploy both master and slave nodes. In future version, they will run from the master node to deploy master and slave nodes.
	
### Things to do before deployment

- Install python
- Add the public key of the machine running the playbook to all the nodes.

### Prerequisites

- Deploy against Debian 8.0 node
- Make sure `python` is installed on the target nodes
- Ansible version used is `1.9.1`

### How to deploy

```bash
$ ansible-playbook -v playbooks/install.yml
```
