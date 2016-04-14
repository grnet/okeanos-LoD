# Service VM image creation

## Description

This guide describes how to generate and publish a Lambda service VM images on the ~okeanos public cloud. In order to create the image file a custom script that uses `snf-image-creator` in the backend has been developed.

### The create_image.sh shell script

The script responsible for creating a Service VM image. It must be run on a service VM. It sets up the default site, enables the ansible-vm-init init script, then runs snf-image-creator, to bundle the host. We will use this script in Step 6 below. 

## Steps

1. Install the Fokia library. To install Fokia and its dependencies, consult the [installation guide](../fokia/usage.md).
2. Navigate to the Service VM manager folder: `cd <project_directory>/webapp/manager`.
3. Create a new Service VM, by issuing the following command:
```python service_vm_manager.py --action image_creation --project-name <~okeanos project name> --auth-token <~okeanos auth token>```
4. After the service_vm_manager finishes successfully, login to the created VM using ssh.
5. Navigate to the following folder on the Service VM: 
```cd /var/www/okeanos-LoD/webapp/image```
6. Execute `./create_image.sh`.
7. snf-image-creator will run behind the scenes to bundle the host. Insert the required image properties, and
~okeanos credentials, to register your new image on the ~okeanos cloud. 

The recommended image name to use is `Lambda Service VM YYYYMMDD` (e.g. `Lambda Service VM 20151219`). 

For more information about using snf-image-creator, consult the [relevant documentation](https://www.synnefo.org/docs/snf-image-creator/latest/usage.html#dialog-based-version).

