# ~okeanos LoD backend service Ansible

## Description
In this directory you can find the Ansible code that deployes the backend service vm
used by ~okeanos Lambda on Demand project.

## Prerequisites
To use this code you need:

1. A vm running Debian OS.
2. The vm should have a public ip.
3. Python should be installed on the vm.

## Tasks

### rabbitmq
- Downloads and installs rabbitmq-server with aptitude.

### celery
- Install python-pip.
- Installs celery using pip.

## Usage
To use this code, run

`ansible-playbook -v playbooks/setup.yml -i <inventory>`

The vms should be under `service-vms` group in the inventory file.

## Results
This Ansible code will install and configure Apache server, Django, PostgreSQL, Celery with RabbitMQ and Supervisord.
It will create two Celery queues and start a worker for each queue. These workers run under supervisord and thus, they
can be stopped and started through it. An init script will be added to the boot and shutdown sequences of the vm so that
Supervisord is started and stopped when the vm boots or shuts down respectively. This is done so that the workers will
be up and running when the vm boots and stopped when the vm shuts down. Ansible will also clone ~okeanos-LoD
repository from Github and set Apache server to serve ~okeanos-LoD webapp.

To check that everything is installed correctly after running the Ansible code, open a web browser and
enter your vm's public ip on the address bar. You should see the following text:

```
It worked!
Congratulations on your first Django-powered page.

Of course, you haven't actually done any work yet. Next, start your first app by running python manage.py startapp [app_label].

You're seeing this message because you have DEBUG = True in your Django settings file and you haven't configured any URLs. Get to work!
```
