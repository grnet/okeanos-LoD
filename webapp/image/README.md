# Service VM image creation

## Description

The scripts contained in the webapp/image directory are responsible for assisting an
administrator in creating a new Service VM image.

### ansible-vm-init

The run-once init script responsible for  the initial configuration of the Service VM, after it has
been created using the image. It runs ansible on localhost, using local connection, and including
 the tags necessary for the initial configurations. Then, after a successful run, the init script
 disables and deletes itself.

### index.html

The default apache page. It contains the AdminLTE template, and is used as a waiting page for the
 user, while his Service VM initializes. The page auto-refreshes every 20 seconds, so that when
 the Service VM has been configured, the Lambda webpage appears.

### setup_default_site.sh

Script responsible for setting up the default apache page. It copies the index.html, along with
the necessary js/css/image files, taken from the ember project directories.

### create_image.sh

Script responsible for creating a Service VM image. It must be run on a service VM. It sets up
the default site, enables the ansible-vm-init init script, then runs snf-image-creator, to bundle
 the host.

## Usage

1. Create a new Service VM, by issuing:
`python webapp/manager/service_vm_manager.py --action image_creation`.
2. After the service_vm_manager finishes successfully, ssh to the created VM.
3. Navigate to the image folder on the Service VM: `cd /var/www/okeanos-LoD/webapp/image`.
4. Run `./create_image.sh`.
5. snf-image-creator will run, to bundle the host. Insert the required image properties, and
~okeanos credentials, to register your new image on the ~okeanos cloud. Recommended image
name/description: Lambda Service VM YYYYMMDD (e.g. Lambda Service VM 20151219).
