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
department=$2
project_path=/Users/j/MRI_DATA/${department}/${project_id}
log=${project_path}/derivatives/bidsonly/xnatpull.log
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
    docker run \
    -it \
    -e project_id=${project_id} \
    --name=`echo ${auth_service_name}` \
    --mount type=bind,source=${token_path_doctor},destination=${token_path_container},readonly=false \
     ${auth_image} 
    #  >> ${log} 2>&1 &;
fi
