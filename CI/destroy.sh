#!/bin/bash

# ~okeanos token is given as first argument.
okeanos_token=$1

# Source the python virtual environment.
source okeanos_lod_python_environment/bin/activate

# Get the id of the Central VM.
central_vm_id=$(python utils.py --get=id --vm_name="central_service" --auth_token=$okeanos_token)

# Destroy the Central VM.
cd okeanos-LoD/central_service/manager
python central_service_manager.py --action=destroy --auth_token=$okeanos_token --vm_id=$central_vm_id --public_key_path=./.ssh/id_rsa.pub --private_key_path./.ssh/id_rsa
cd ../../../

# Destroy the lambda instance.
echo "$(python manage_lambda_instance.py --action=destroy --service_vm_name="Service VM" --auth_token=$okeanos_token)"

# Get the id of the Service VM.
service_vm_id=$(python utils.py --get=id --vm_name="Service VM" --auth_token=$okeanos_token)

# Destroy the Service VM.
cd okeanos-LoD/webapp/manager
python service_vm_manager.py --action=destroy --auth_token=$okeanos_token --vm_id=$service_vm_id --public_key_path=./.ssh/id_rsa.pub --private_key_path./.ssh/id_rsa
cd ../../../

# Destroy the python virtual environment.
rm -r okeanos_lod_python_environment

# Delete the public and private keys.
rm ./.ssh/id_rsa
rm ./.ssh/id_rsa.pub

# Delete the cloned repository.
$(yes | rm -r okeanos-LoD/)

# Deactivate the virtual environment.
deactivate

