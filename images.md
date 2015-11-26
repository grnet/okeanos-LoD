# Lambda Instance images creation

## Description

Using the fokia library, an administrator is able to create updated images for the Lambda Instance Master and Slave nodes.

## Usage

1. To create the Lambda Instance images, one must use the fokia library. This can be done either on your own computer, after installing the required dependencies, or using an up-to-date Lambda Service VM.
2. Navigate to the fokia library folder: `cd <project_directory>/core/fokia`.
3. Run `python lambda_instance_manager.py --image-creation --project-name <~okeanos project name> --auth_token <~okeanos auth token>`, to create a minimal Lambda Instance suitable for image creation.
4. After lambda_instance_manager finishes the Lambda Instance creation successfully, a Lambda Master and a Lambda Slave node will be available on your cyclades account. You will be able to ssh  into their root user, from the system, where you run the lambda_instance_manager.
5. To be able to upload the Lambda Slave image to the ~okeanos cloud, you must assign a public IP to the slave node<sup>[1](#footnote1)</sup>.
6. ssh into the Master and Slave nodes. On each host, run:
  1. `rm /root/*` (Optional step, to remove downloaded packages and minimize image size)
  2. `snf-image-creator /`
7. snf-image-creator will run, to bundle the host. Insert the required image properties, and ~okeanos credentials, to register your new image on the ~okeanos cloud. Recommended Lambda Master image name/description: Lambda Master YYYYMMDD (e.g. Lambda Master 20151219). Recommended Lambda Slave image name/description: Lambda Slave YYYYMMDD (e.g. Lambda Slave 20151219).
8. Edit the `webapp/ansible/roles/service-vm/templates/settings.py.j2` file, changing the MASTER_IMAGE_ID and SLAVE_IMAGE_ID variables to the new image ids<sup>[2](#footnote2)</sup>.

<a name="footnote1"><sup>1</sup></a> There is a bug that causes a public IP not to attach correctly, if the node has previously been attached to a private network. In that case, de-attach the Lambda Slave node from the lambda-vpn, attach the public IP, then re-attach it to the lambda-vpn.

<a name="footnote2"><sup>2</sup></a> To get the ~okeanos image ids, one can issue `kamaki image list`.
