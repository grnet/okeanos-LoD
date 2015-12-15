# Central ~okeanos Lambda on Demand(LoD) Service Ansible

## Description
In the current directory, you can find the Ansible code that deploys the Central ~okeanos LoD
Service VM, used to gather metrics about the usage of ~okeanos Lambda on Demand Service across the
~okeanos infrastructure.

## Prerequisites
To use this code you need:

1. A VM upon ~okeanos infrastructure, running Debian OS.
2. The VM should have a public IP.
3. Python should be installed on the VM.

## Usage
There are two ways to use this code. The first one, is when there is no previous installation of
the Central ~okeanos Service on the VM and the second one is when you want to update an existing
installation. We will describe each one in the next paragraphs.

### Clean Installation
To deploy the Central ~okeanos LoD Service on a VM, run

`ansible-playbook -v playbooks/setup.yml -i <inventory>`

where `<inventory>` should be replaced with the name of your inventory file. As an example of an
inventory file, we provide the `hosts` file. Note that every host that you want Ansible to run on
should be under `[central-vm]` group. In case you want to use our `hosts` file, you should replace
the `XXXXXX` with the ~okeanos id of the VM you want Ansible to run on.

#### SSL Certificate
When deploying a new Central ~okeanos LoD Service VM, you need to provide a certificate from a
trusted authority. Before running Ansible, you should place the `SSL Certificate File`,
`SSL Certificate Key File` and `SSL Certificate Chain File` inside `roles/central-vm/files/`
directory. You should also change the names of these file as follows:

SSL Certificate File: `snf-XXXXXX.vm.okeanos.grnet.gr.crt`  
SSL Certificate Key File: `snf-XXXXXX.vm.okeanos.grnet.gr.key`  
SSL Certificate Chain File: `DigiCertCA.crt`

### Update Existing Installation
To update an existing Central ~okeanos LoD Service installation(fetch and deploy updates from the
~okeanos-LoD Github repository) you should first connect over ssh to the VM and run the following
commands, as root user, to shutdown `supervisord`

```bash
supervisorctl stop all
supervisorctl shutdown
```
and then, run

`ansible-playbook -v playbooks/setup.yml -i <inventory> --tags update`

where `<inventory>` should be replaced with the name of your inventory file.

When choosing to update an existing installation, only a portion of the Ansible tasks will be
executed.

In any case and in order to get information regarding which tasks will be run and on which hosts,
you can always run

`ansible-playbook -v playbooks/setup.yml -i <inventory> --list-tasks --list-hosts`

#### Note:
Updating an existing installation should be done with caution. Concretely, there might be updates
that must be performed manually (e.g. a major change on the database model). In case of doubt,
consider consulting the developer that pushed the changed on the Github repository.

## Tasks
The Ansible playbook `setup.yml` will execute six Ansible roles, namely:
- wait_for_ssh (waits until the ssh daemon is up and running on the VM)
- common (installs commonly used packages on the VM, configures users, etc...)
- central-vm (downloads ~okeanos LoD repository from Github, install and configured Apache server,
  installs and configures PostgreSQL database)
- rabbitmq (installs and configures RabbitMQ)
- ember (installs and configures Ember.js)
- celery (installs and configures Celery)

## Results
After Ansible has successfully finished, you can visit Central ~okeanos LoD Service web pages using
a browser and the url

`https://snf-XXXXXX.vm.okeanos.grnet.gr`

where `XXXXXX` should be replaced with the ~okeanos id of your VM.
