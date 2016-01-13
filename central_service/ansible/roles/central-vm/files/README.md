## Description
When deploying a new Central ~okeanos LoD Service VM, you need to provide a certificate from a trusted authority.
Before running Ansible, you should place the SSL Certificate File, SSL Certificate Key File and SSL Certificate Chain File
inside roles/central-vm/files/ directory. You should also change the values of the respective variables inside
roles/central-vm/vars/main.yml to the names of the provided files.
