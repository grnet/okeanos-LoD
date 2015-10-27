# ~okeanos Lambda on Demand backend service

## Description
In this directory you can find the code for the ~okeanos-LoD backend service. It
is implemented as a Django project and currently contains `backend` application.
The backend code can be deployed using the Ansible code inside `ansible/` directory.

## Notes
Before using ansible, make sure you change the value of `central_vm_ip` parameter in
`ansible/roles/service-vm/vars/main.yml` to point to a working Central Service VM.

