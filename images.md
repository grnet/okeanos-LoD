# Lambda Instance images creation

## Description

Using the fokia library, an administrator is able to create new Lambda Instance Master and Slave nodes on the ~okeanos infrastructure, that will have all services installed, but not configured or started. Then, he can use the snf-image-creator tool to create updated images to be published.

## Usage

1. To create the Lambda Master and Slave nodes suitable for Lambda Instance images creation, one must use the fokia library. This can be done either on your own computer, after installing the required dependencies, or using an up-to-date Lambda Service VM. To install fokia and its dependencies on your own computer, consult [\<project_directory\>/core/README.md] (https://github.com/grnet/okeanos-LoD/blob/master/core/README.md).
2. Navigate to the fokia library folder: `cd <project_directory>/core/fokia`.
3. Run `python lambda_instance_manager.py --image-creation --project-name <~okeanos project name> --auth_token <~okeanos auth token>`, to create a minimal Lambda Instance (1 Master and 1 Slave node) suitable for image creation (services are not configured or started, when using the --image-creation flag).
4. After lambda_instance_manager finishes the Lambda Instance creation successfully, a Lambda Master and a Lambda Slave VM will be available on your cyclades account. You will be able to ssh  into their root user, from the system, where you run the lambda_instance_manager.
5. To be able to upload the Lambda Slave image to the ~okeanos cloud, you must assign a public IP to the Slave node<sup>[1](#footnote1)</sup> (the Master node already has a public IP by default).
6. ssh into the Master and Slave nodes. On each host, run:
  1. `rm /root/*` (Optional step, to remove downloaded packages and minimize image size)
  2. `snf-image-creator /`
7. snf-image-creator will run, to bundle the host. Insert the required image properties, and ~okeanos credentials, to register your new image on the ~okeanos cloud. Recommended Lambda Master image name/description: Lambda Master YYYYMMDD (e.g. Lambda Master 20151219). Recommended Lambda Slave image name/description: Lambda Slave YYYYMMDD (e.g. Lambda Slave 20151219). For more information about using snf-image-creator, consult its [documentation] (https://www.synnefo.org/docs/snf-image-creator/latest/usage.html#dialog-based-version).
8. Edit the `webapp/ansible/roles/service-vm/templates/settings.py.j2` file, changing the MASTER_IMAGE_ID and SLAVE_IMAGE_ID variables to the new image ids<sup>[2](#footnote2)</sup>.

<a name="footnote1"><sup>1</sup></a> There is a bug that causes a public IP not to attach correctly, if the node has previously been attached to a private network. In that case, de-attach the Lambda Slave node from the lambda-vpn, attach the public IP, then re-attach it to the lambda-vpn.

<a name="footnote2"><sup>2</sup></a> To get the ~okeanos image ids, one can issue `kamaki image list`.
