#!/bin/bash

#####
## Bash script to destroy everything that create.sh script has created.
##
## Requirements: ~okeanos-LoD Fokia package,
##               virtual-env package,
##               python-dev package,
##               git package.
##
## Usage:
## ./destroy.sh <okeanos_token> <public_key_path> <private_key_path>
##
## Parameters:
## okeanos_token: ~okeanos API token.
## public_key_path: path to a public ssh key.
## private_key_path: path to the private ssh key related with the public ssh key provided.
##
## Description:
## Upon execution, this script will destroy everything that create.sh script has created.
## For more information see the README.md file.
#####

source config.txt

# ~okeanos token is given as first argument.
okeanos_token=$TOKEN

# Public key path is given as second argument.
public_key_path=$PUBLIC_KEY_PATH

# Private key path is given as third argument.
private_key_path=$PRIVATE_KEY_PATH

# Clone devel branch of ~okeanos-LoD project.
git clone -b devel https://github.com/grnet/okeanos-LoD.git

# Create a python virtual environment and source it.
virtualenv okeanos_lod_python_environment
source okeanos_lod_python_environment/bin/activate

# Install Fokia and its requirements.
cd okeanos-LoD/core
pip install -r requirements.txt
python setup.py install
cd ../../

# Get the id of the Central VM.
central_vm_id=$(python utils.py --get id --vm_name "Central VM devel CI" --auth_token $okeanos_token)

# Destroy the Central VM.
cd okeanos-LoD/central_service/manager
python central_service_manager.py --action destroy --auth_token $okeanos_token --vm_id $central_vm_id --public_key_path "$public_key_path" --private_key_path "$private_key_path"
cd ../../../

# Destroy the lambda instance.
echo "$(python manage_lambda_instance.py --action destroy --service_vm_name "Service VM devel CI" --auth_token $okeanos_token)"

# Get the id of the Service VM.
service_vm_id=$(python utils.py --get id --vm_name "Service VM devel CI" --auth_token $okeanos_token)

# Destroy the Service VM.
cd okeanos-LoD/webapp/manager
python service_vm_manager.py --action destroy --auth_token $okeanos_token --vm_id $service_vm_id --public_key_path "$public_key_path" --private_key_path "$private_key_path"
cd ../../../

# Destroy the python virtual environment.
rm -r okeanos_lod_python_environment

# Delete the cloned repository.
$(yes | rm -r okeanos-LoD/)

# Deactivate the virtual environment.
deactivate

