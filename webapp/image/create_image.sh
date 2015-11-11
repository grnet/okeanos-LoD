#!/bin/bash

# Setup default site
/var/www/okeanos-LoD/webapp/image/setup_default_site.sh &&

# Copy and enable run-once init script
cp /var/www/okeanos-LoD/webapp/image/ansible-vm-init /etc/init.d/ &&
update-rc.d ansible-vm-init start 3 &&

# Run snf-image-creator
snf-image-creator /

