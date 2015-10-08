#!/bin/bash

#####
## Bash script to destroy an ~okeanos Central Service VM.
##
## Requirements: ~okeanos-LoD Fokia package.
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
## Upon execution, this script will destroy the ~okeanos Central Service VM based on its
## name(central_service).
#####

# ~okeanos token is given as first argument.
okeanos_token=$1

# Public key path is given as second argument.
public_key_path=$2

# Private key path is given as third argument.
private_key_path=$3

# Source the python virtual environment.
source okeanos_lod_python_environment/bin/activate

# Get the id of the Central VM.
central_vm_id=$(python utils.py --get id --vm_name "central_service" --auth_token $okeanos_token)

# Destroy the Central VM.
cd okeanos-LoD/central_service/manager
python central_service_manager.py --action destroy --auth_token $okeanos_token --vm_id $central_vm_id --public_key_path "$public_key_path" --private_key_path "$private_key_path"
cd ../../../

# Delete the cloned repository.
$(yes | rm -r okeanos-LoD/)

# Deactivate the virtual environment.
deactivate

