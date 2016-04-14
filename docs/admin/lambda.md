# Lambda Instance images creation

## Description

This guide describes how to generate and publish Lambda master and slaves images on the ~okeanos public cloud.

In the steps that follow we will use the `snf-image-creator` tool to create and publish the images.


## Steps


1. Install the Fokia library. To install Fokia and its dependencies, consult the [installation guide](../fokia/usage.md).
2. Navigate to the fokia library folder: `cd <project_directory>/core/fokia`.
3. In order to bootstrap a minimal Lambda Instance (1 master and 1 slave node), which we will use for the image creation, execute the following command:
```python lambda_instance_manager.py --image-creation --project-name <~okeanos project name> --auth-token <~okeanos auth token>```
(Note that no services will be started on these two hosts as we are using the --image-creation flag.)
4. After `lambda_instance_manager.py` finishes a Lambda master and slave nodes will be available on your cyclades account. You will be able to login using ssh from the system, where you run the `lambda_instance_manager.py` command.
5. To be able to upload the Lambda slave image to the ~okeanos cloud, you must assign a public IP to the slave node<sup>[1](#footnote1)</sup> (the master node already has a public IP by default).
6. Login (using ssh) onto the Lambda master and slave nodes respectively. On each host, execute:
```rm -f /root/* && snf-image-creator /```
7. `snf-image-creator` will run and bundle the host. Insert the required image properties, and ~okeanos credentials, to register your new image on the ~okeanos cloud. The recommended Lambda master image name to use is: `Lambda master YYYYMMDD` (e.g. `Lambda master 20151219`). The recommended Lambda slave image name to use is: `Lambda slave YYYYMMDD` (e.g. `Lambda slave 20151219`). For more information about using snf-image-creator, consult the [relevant documentation](https://www.synnefo.org/docs/snf-image-creator/latest/usage.html#dialog-based-version).
8. On the source code repository edit the `webapp/ansible/roles/service-vm/templates/settings.py.j2` file, changing the `MASTER_IMAGE_ID` and `SLAVE_IMAGE_ID` variables to the new image ids<sup>[2](#footnote2)</sup> for your changes to take effect. 

<a name="footnote1"><sup>1</sup></a> There is a bug that causes a public IP not to attach correctly, if the node has previously been attached to a private network. In that case, de-attach the Lambda slave node from the lambda-vpn, attach the public IP, then re-attach it to the lambda-vpn.

<a name="footnote2"><sup>2</sup></a> To get the ~okeanos image ids, one can issue `kamaki image list`.
