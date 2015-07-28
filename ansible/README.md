# Lambda Cluster Ansible Setup


## Things to do before deployment

- Install python on every node.
- Add the public key of the machine running the playbooks to all the nodes.
- Create a private network among the machines.
- Modify ansible/hosts file to include the master-node and all the slave nodes.
- Modify ansible/host_vars/master-node file. Concretely, change the internal_ip variable.
- For each slave in ansible/hosts, create a file in ansible/host_vars (the name of the slave in ansible/hosts should be the name of the file in ansible/host_vars). Inside
the file, define the internal_ip variable and the id variable. Each slave should have a unique id.
- Make sure that the firewall of the master-node is off.
- Make sure that the values in vars/main.yml in each role, are correctly defined. For example,
if you have 2 slaves, you should create, at most, 2 TaskManagers in flink and not 3.


## Prerequisites

- Deployed against Debian 8.0 node.
- Ansible version used is 1.9.1.
- Currently, the playbooks should be run from an external machine to setup both the master and the slave nodes. In future version, they will be run from the master node to setup
both the master and the slaves.


## Playbooks and Roles

There are four (4) roles and five (5) playbooks. These are:
- proxy role, run from proxy playbook.
- common role, run from common playbook.
- apache-hadoop role, run from apache-hadoop playbook.
- apache-kafka role, run from apache-kafka playbook.
- apache-flink role, run from apache-flink playbook.
- cluster-install playbook which runs all the roles with the above sequence.


## Role Explanation


### proxy
- Installs squid http proxy on master node, using apt package manager.
- Configures the acls of the proxy, and sets the localnet to allowed.
- Restarts the http proxy service


### common

- Installs all the packages that are needed in order for the cluster to run.
- Creates the needed environment variables.
- Configures the /etc/hosts file.


### apache-hadoop
- Downloads and installs Apache Hadoop.
- Formats HDFS.
- Starts HDFS.
- Creates the required directories on HDFS.
- Starts Yarn.


### apache-kafka
- Downloads and installs Apache Kafka.
- Starts Apache Zookeeper on master node.
- Starts an Apache Kafka server on every node.
- Creates the needed input and output topics.


### apache-flink
- Downloads and installs Apache Flink on master node.
- Starts and Apache Flink, Yarn session.




## How to deploy

You can deploy the whole cluster by running the cluster-install playbook:

```bash
$ ansible-playbook playbooks/cluster/cluster-install.yml -i hosts
```

or, you can run a single playbook, e.g.:

```bash
$ ansible-playbook playbooks/apache-hadoop/hadoop-install.yml -i hosts
```
