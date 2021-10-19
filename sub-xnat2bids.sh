#!/bin/env bash

# Usage: bash sub-xnat2bids.sh <project ID>
project_id=$1
project_path=/MRI_DATA/nyspi/${project_id}
token_path_doctor=${project_path}/.tokens
xnat2bids_image=doc_xnat2bids:latest
auth_image=doc_xnat_auth:latest
auth_service_name=xnat_auth_${project_id}
xnat2bids_service_name=xnat2bids_${project_id}
docker container rm ${auth_service_name}
docker container rm ${xnat2bids_service_name}
# docker pull ${xnat2bids_image}

# Ensure authentication requirements are met before 
# anything else.

# If valid credentials don't exist, call auth.py
# The project's xnat password is encrypted
# by auth.py using a 2048 bit RSA key (Code used to 
# generate at the bottom of auth.py) and a randomly
# generated 16 character string. auth.py takes no arguments, 
# and places this token file in the folder .../<project ID>/.tokens

token_file=${token_path_doctor}/xnat2bids_${project_id}_login.bin

# -s flag for any file that is not empty, -r for readable, -e any type
if test -s "$token_file"; then
    echo Located token_file ${token_file}
else
    auth_service_name=xnat_auth_${project_id}
    echo Token ${token_file} not found--trying to run auth container.
    # touch token_file
    # docker pull {auth_image}
    docker run \
    -e project_id=${project_id} \
    --name=${auth_service_name} \
    -it \
    -v ${project_path}/.tokens:/tokens \
    -v /.xnat:/xnat \
    ${auth_image};
fi

# TODO: do we need to worry about permissions aka
# a rogue user falsely creating auths for a different project?

# TODO: determine central location of the public key and 
# how to control access to it
# ---> rn it's in the docker image ("jackgray/xnat-auth") 
# TODO: security concerns there?

# Consideration: retrieve JSESSION token before launching service,
# encrypt it, then send that token -- update: doesn't seem to be necessary
# python3 decrypt.py

bidsonlypath_doctor=${project_path}/derivatives/bidsonly 
bidsonlypath_container=/derivatives/bidsonly 
rawdata_path_doctor=${project_path}/rawdata 
rawdata_path_container=/rawdata 
workinglistpath_doctor=${project_path}/scripts/${project_id}_working.lst
workinglistpath_container=/scripts/${project_id}_working.lst
token_path_doctor=${project_path}/.tokens
token_path_container=/tokens
private_path_doctor=/.xnat/xnat2bids_private.pem
private_path_container=/xnat/xnat2bids_private.pem
# ^ btwn the RSA import func and distroless something doesn't like .folder names 
# (does not seem to be an issue with bloatier official python3 image above)

image_name=jackgray/xnat2bids:latest
service_name=xnat2bids_${project_id}

docker run \
-it \
-e project_id=${project_id} \
--name=${service_name} \
-v ${rawdatapath_doctor}:${rawdatapath_container} \
-v ${bidsonlypath_doctor}:${bidsonlypath_container} \
-v ${workinglistpath_doctor}:${workinglistpath_container} \
-v ${token_path_doctor}:${token_path_container} \
-v ${private_path_doctor}:${private_path_container} \
${xnat2bids_image};