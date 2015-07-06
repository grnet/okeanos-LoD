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


## Apache Flink deployment

Contains Ansible playbook for the deployment of Apache Flink. The playbook is split into five (5) tasks:
- Download Apache Flink, Yarn version(downloads Apache Flink into /root).
- Uncompress Apache Flink(uncompresses Apache Flink into /usr/local).
- Create softlink for Apache Flink(creates /usr/local/flink softlink).
- Configure Apache Flink(copies pre-created Apache Flink configuration files into /usr/local/flink/conf).
- Start Apache Flink(starts an Apache Yarn session with 2 TaskManagers and 512 MB of RAM each).

Apache Flink needs to be installed only on master node. Information about the architecture of the cluster(number of slaves, etc...) are found through Apache Yarn.

### How to deploy

```bash
$ansible-playbook -v playbooks/apache-flink/flink-install.yml
```


## Apache Kafka deployment

Contains Ansible playbook for the deployment of Apache kafka. The playbook uses the apache-kafka role to install Apache Kafka on a cluster of machines. The following
actions are performed on a single node, acting as the master of the cluster:
- Download Apache Kafka(downloads Apache Kafka into /root).
- Uncompress Apache Kafka(uncompresses Apache Kafka into /usr/local).
- Create softlink for Apache Kafka(creates /usr/local/kafka softlink).
- Configure Apache kafka(copies pre-created Apache Kafka configuration files to /usr/local/kafka/config).
- Start Apache Zookeeper server(starts an Apache Zookeeper server which is a prerequisite for Apache Kafka server).
- Wait for Apache Zookeeper to become available.
- Start Apache Kafka server(starts an Apache Kafka server).
- Wait for Apache Kafka server to become available.

The following actions are performed on a configurable number of nodes, acting as the slaves of the cluster:
- Download Apache Kafka(downloads Apache Kafka into /root).
- Uncompress Apache Kafka(uncompresses Apache Kafka into /usr/local).
- Create softlink for Apache Kafka(creates /usr/local/kafka softlink).
- Configure Apache kafka(copies pre-created Apache Kafka configuration files to /usr/local/kafka/config).
- Start Apache Kafka server(starts an Apache Kafka server).
- Wait for Apache Kafka server to become available.

After the installation is completed, both on the master and the slaves, the following actions are performed:
- Create Apache Kafka input topic(creates an Apache Kafka topic, named "input", to store input data).
- Create Apache Kafka batch output topic(creates an Apache Kafka topic, named "batch-output", to store the output data of the batch job).
- Create Apache Kafka stream output topic(creates an Apache Kafka topic, named "stream-output", to store the output data of the stream job).

The replication of each of the above topics, is equal to the number of slaves, plus 1 for the master.

The inventory file should contain the following information:
- The name of the master node(if different from "master-node", then the role's commands should be changed accordingly).
- A variable named "kafka-ip" under the "master-node" to define the IP address that will be used for Apache Kafka traffic.
- A variable named "id" under each slave node, defining a unique integer number for each slave.

Currently, the playbook is run from an external node, and deploy both master and slave nodes. In future version, they will run from the master node to deploy the slave nodes.

### How to deploy

```bash
$ansible-playbook -v playbooks/apache-kafka/kafka-install.yml
```

