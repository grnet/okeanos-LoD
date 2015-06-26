# Ansible Cluster Setup


## Things to do before deployment

- Install python
- Add the public key of the machine running the playbook to all the nodes.


## Prerequisites

- Deploy against Debian 8.0 node
- Make sure `python` is installed on the target nodes
- Ansible version used is `1.9.1`


## VM packages and variable setup

Contains Ansible playbook for the installation of required packages and variables. The play is split into three (3) tasks:
- install packages and run basic commands on newly created vms.
- fetch public ssh key from master.
- distribute public key to all slave nodes.
Currently, the playbooks are run from an external node, and deploy both master and slave nodes. In future version, they will run from the master node to deploy master and slave nodes.
	
### How to deploy

```bash
$ ansible-playbook -v playbooks/install.yml
```


## Hadoop services (HDFS & YARN) deployment

Contains Ansible playbook for the deployment of the Hadoop services required for Flink (HDFS and YARN services). The play is split into five (5) tasks:
- install (downloads and untars hadoop into /usr/local, makes softlink to /usr/local/hadoop)
- config (creates and copies appropriate hadoop configuration, using the master and slaves defined in the inventory)
- hdfs_format (initial format of hdfs)
- hdfs_dirs (create of appropriate hdfs directories, currently for user root)
- start (start hdfs & yarn demons on the cluster nodes)
Currently, the playbooks are run from an external node, and deploy both master and slave nodes. In future version, they will run from the master node to deploy the slave nodes.

### How to deploy

```bash
$ ansible-playbook -v playbooks/hadoop.yml
```
