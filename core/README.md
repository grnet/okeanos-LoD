# Core python library


## Description

The libraries contained in the core package are responsible for creating a cluster of VMs and installing all the required packages and configs to have a complete lambda instance. A description of the libraries follows:

### provisioner

The library is responsible for creating a VM cluster, using the Kamaki python API. It reads the authentication info from the .kamakirc, and accepts the cluster specs as arguments.

### ansible_manager

The library is responsible for managing the ansible, that will run on the cluster. Its tasks are:
* It reads a dictionary, containing the necessary info about the cluster and its nodes
* It creates an ansible inventory object, using the dictionary
* It creates the necessary group and host vars, required for ansible to run on all the nodes and configure them properly
* It sets some ansible constants, required eg for SSH tunnelling through the master node
* It runs ansible playbooks using the previously mentioned inventory and constants

### cluster_creator

The script is responsible for creating the entire lambda instance.
* It sets the provisioner arguments (cluster specs), then calls the provisioner to create the cluster.
* After that, it gets the output dictionary of the provisioner and adds some more values to it, which are obtained using the provisioner, after the cluster creation.
* It calls the ansible_manager, to create the inventory, using the dictionary as input.
* Finally, it uses the created manager object (containing the inventory and constants), to run the required playbooks in the correct order, to create the lambda instance.

## Prerequisites

* kamaki 0.13.4 or later
* ansible 1.9.2 or later
* crypto 1.4.1 or later


## Installation

- Create a .kamakirc configuration in your home folder and add all the required configurations.
 Here is an example configuration
```
[global]
default_cloud = lambda
; ca_certs = /path/to/certs

[cloud "lambda"]
url = https://accounts.okeanos.grnet.gr/identity/v2.0
token = your-okeanos-token
```
Note that you may retrieve your ~okeanos API token, after logging into the service, by visiting [this page][api_link]. 

- Install required packages. Within the `core` directory execute `sudo pip install -r requirements.txt`.
- Install package using `sudo python setup.py install`

## Usage


To create a lambda instance, one must run `python cluster_creator.py` from within the `core/fokia` directory. To change the default settings (one master instance and one slave instance) one has to edit the `cluster_creator.py` script prior to executing it. 



## Testing

To test the library we use `tox`. In order to run the tests:

- Make sure you have tox installed `pip install tox`
- Run `tox`

This will automatically create the testing environments required and run the tests

[api_link]: https://accounts.okeanos.grnet.gr/ui/api_access