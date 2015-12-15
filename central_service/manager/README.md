# Central ~okeanos Lambda on Demand(LoD) Service Manager

## Description
Inside this folder you can find the `central_service_manager.py` script that can be used to setup
a VM upon ~okeanos infrastructure and also deploy the Ansible playbooks and roles needed for the
Central ~okeanos LoD Service.

## Usage
To get information regarding how `central_service_manager.py` script can be used, run

```
python central_service_manager.py -h
```

and an appropriate message will be displayed regarding the arguments of the script. The output will
be similar to

```
usage: central_service_manager.py [-h] --action {create,start,stop,destroy}
                                  [--auth-token AUTH_TOKEN] [--vm-id VM_ID]
                                  [--vm-name VM_NAME] [--vcpus {1,2,4,8}]
                                  [--ram {512,1024,2048,4096,6144,8192}]
                                  [--disk {5,10,20,40,60,80,100}]
                                  [--project-name PROJECT_NAME]
                                  [--private-key-path PRIVATE_KEY_PATH]
                                  [--public-key-path PUBLIC_KEY_PATH]

Central service VM provisioning

optional arguments:
  -h, --help            show this help message and exit
  --action {create,start,stop,destroy}
                        action to be performed
  --auth-token AUTH_TOKEN
                        the ~okeanos authentication token of the user
  --vm-id VM_ID         the ~okeanos id of the correspoding VM
  --vm-name VM_NAME     the name of the VM
  --vcpus {1,2,4,8}     the number of CPUs on the VM
  --ram {512,1024,2048,4096,6144,8192}
                        the amount of RAM on the VM
  --disk {5,10,20,40,60,80,100}
                        the size of the HDD on the VM
  --project-name PROJECT_NAME
                        the ~okeanos project with the appropriate quotas for
                        the VM
  --private-key-path PRIVATE_KEY_PATH
                        path to private ssh key to be used by Ansible (should
                        pair with the provided public key)
  --public-key-path PUBLIC_KEY_PATH
                        path to public ssh key to be injected in the VM
                        (should pair with the provided private key)
```

with some parameters possibly varying.

## Requirements
Fokia library should be installed on your system in order to use `central_service_manager` script.
A user may install and use the library (through CLI) following the guidelines [here][ref1].

[ref1]: ../../core
