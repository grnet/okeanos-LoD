#!/bin/bash

# ~okeanos token is given as first argument.
okeanos_token=$1

# Public key path is given as second argument.
public_key_path=$2

# Private key path is given as third argument.
private_key_path=$3

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
python service_vm_manager.py --action create --auth_token $okeanos_token --public_key_path "$public_key_path" --private_key_path "$private_key_path"
cd ../../../

# Create a Lambda Instance.
echo "$(python manage_lambda_instance.py --action create --service_vm_name "Service VM" --auth_token $okeanos_token)"

# Create a Central VM.
cd okeanos-LoD/central_service/manager
python central_service_manager.py --action create --auth_token $okeanos_token --public_key_path "$public_key_path" --private_key_path "$private_key_path"
cd ../../../

# Applications #

# Deactivate the virtual environment.
deactivate

