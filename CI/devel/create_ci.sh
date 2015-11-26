#!/bin/bash

#####
## Bash script to fully deploy ~okeanos-LoD Service.
##
## Requirements: ~okeanos-LoD Fokia package,
##               virtual-env package,
##               python-dev package,
##               git package.
##
## Usage ./create <okeanos-token> <public_key_path> <private_key_path>
##
## Parameters:
## okeanos_token: ~okeanos API token.
## public_key_path: path to a public ssh key.
## private_key_path: path to the private ssh key related with the public ssh key provided.
##
## Description:
## Upon execution, this script will fully deploy ~okeanos-LoD Service. For more information
## see the README.md file.
#####

source config.txt

# ~okeanos token is given as first argument.
okeanos_token=$TOKEN

# Public key path is given as second argument.
public_key_path=$PUBLIC_KEY_PATH

# Private key path is given as third argument.
private_key_path=$PRIVATE_KEY_PATH

# Project to use
okeanos_project="lambda.grnet.gr"

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

# Create a Service VM.
cd okeanos-LoD/webapp/manager
python service_vm_manager.py --action create --auth-token $okeanos_token --public-key-path "$public_key_path" --private-key-path "$private_key_path" --vm-name "Service VM devel CI" --project-name $okeanos_project
cd ../../../

# Create a Lambda Instance.
echo "$(python manage_lambda_instance.py --action create --service_vm_name "Service VM devel CI" --auth_token $okeanos_token)"

# Create a Central VM.
cd okeanos-LoD/central_service/manager
python central_service_manager.py --action create --auth-token $okeanos_token --public-key-path "$public_key_path" --private-key-path "$private_key_path" --vm-name "Central VM devel CI" --project-name $okeanos_project
cd ../../../

# Upload an application to Pithos, deploy in on the lambda instance and start it.
echo "$(python manage_application.py --action upload --service_vm_name "Service VM devel CI" --auth_token $okeanos_token --application stream-1.0-jar-with-dependencies.jar)"
echo "$(python manage_application.py --action deploy --service_vm_name "Service VM devel CI" --auth_token $okeanos_token)"
echo "$(python manage_application.py --action start --service_vm_name "Service VM devel CI" --auth_token $okeanos_token)"

# Deactivate the virtual environment.
deactivate

