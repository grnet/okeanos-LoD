# Flink via Ansible

## Hadoop services (HDFS & YARN) deployment

Contains Ansible playbook for the deployment of the Hadoop services required for Flink (HDFS and YARN services). The play is split into five (5) tasks:
- install (downloads and untars hadoop into /usr/local, makes softlink to /usr/local/hadoop)
- config (creates and copies appropriate hadoop configuration, using the master and slaves defined in the inventory)
- hdfs_format (initial format of hdfs)
- hdfs_dirs (create of appropriate hdfs directories, currently for user root)
- start (start hdfs & yarn demons on the cluster nodes)
Currently, the playbooks are run from an external node, and deploy both master and slave nodes. In future version, they will run from the master node to deploy the slave nodes.
	
### Things to do before deployment

- Edit inventory (hosts file) and define the appropriate master node and slave nodes. Currently, the master also acts as a slave.
- Use ssh-keygen on all nodes. Populate the master public key onto the slaves authorized_keys file. Populate all keys onto all nodes known_hosts file.
- Edit the /etc/hosts file of all nodes, to map the according hostnames to the internal ip addresses (for example 192.168.1.2     snf-661243)  
Note: All the above tasks will be included in the prerequisites playbooks.


### Prerequisites

- Deploy against Debian 8.0 node
- Make sure `python` and `openjdk-7-jdk` is installed on the target nodes
- Ansible version used is `1.9.1`

### How to deploy

```bash
$ ansible-playbook -v playbooks/hadoop.yml
```
