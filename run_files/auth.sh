#!/bin/env bash

# Ensure authentication requirements are met before
# anything else.

# If valid credentials don't exist, call auth.py
# The project's xnat password is encrypted
# by auth.py using a 2048 bit RSA key (Code used to
# generate at the bottom of auth.py) and a randomly
# generated 16 character string. auth.py takes no arguments,
# and places this token file in the folder .../<project ID>/.tokens

project_id=$1
project_path=/MRI_DATA/nyspi/${project_id}
token_path_doctor=${project_path}/.tokens
token_path_container=/tokens
token_file=${token_path_doctor}/xnat2bids_${project_id}_login.bin
auth_image=jackgray/xnat_auth:amd64
auth_service_name=xnat_auth_${project_id}
docker container rm ${auth_service_name}
# -s flag for any file that is not empty, -r for readable, -e any type
if test -s "$token_file"; then
    echo Located token_file ${token_file}
else
    
    echo Token ${token_file} not found--trying to run auth container.
    docker pull ${auth_image}
    # touch token_file
    docker run \
    -it \
    -e project_id=${project_id} \
    --name=${auth_service_name} \
    --mount type=bind,source=${project_path}/.tokens,destination=/tokens,readonly=false \
     ${auth_image};
fi