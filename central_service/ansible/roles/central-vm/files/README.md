## Description
When deploying a new Central ~okeanos LoD Service VM, you need to provide a certificate from a
trusted authority. Before running Ansible, you should place the `SSL Certificate File`,
`SSL Certificate Key File` and `SSL Certificate Chain File` inside this directory. You should also
change the names of these file as follows:

SSL Certificate File: `snf-XXXXXX.vm.okeanos.grnet.gr.crt`  
SSL Certificate Key File: `snf-XXXXXX.vm.okeanos.grnet.gr.key`  
SSL Certificate Chain File: `DigiCertCA.crt`
