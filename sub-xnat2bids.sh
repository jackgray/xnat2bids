#!/bin/bash

# Usage: bash sub-xnat2bids.sh <project ID>

docker rm xnat2bids_patensasc

project_id=$1
project_path=/MRI_DATA/nyspi/${project_id}
bidsonlypath_doctor=/Users/j/${project_path}/derivatives/bidsonly 
bidsonlypath_container=${project_path}/derivatives/bidsonly 
rawdata_path_doctor=/Users/j/${project_path}/rawdata 
rawdata_path_container=${project_path}/rawdata 
workinglistpath_doctor=/Users/j/${project_path}/scripts/${project_id}_working.lst
workinglistpath_container=${project_path}/scripts/${project_id}_working.lst
token_path_doctor=/Users/j/${project_path}/.tokens
token_path_container=${project_path}/.tokens
private_path_doctor=/Users/j/.xnat/xnat2bids_private.pem
private_path_container=/xnat/xnat2bids_private.pem

image_name=jackgray/xnat2bids:latest
service_name=xnat2bids_${project_id}

# Ensure authentication requirements are met before 
# anything else.

# If valid credentials don't exist, call auth.py
# The project's xnat password is encrypted
# by auth.py using a 2048 bit RSA key (Code used to 
# generate at the bottom of auth.py) and a randomly
# generated 16 character string. auth.py takes no arguments, 
# and places this token file in the folder .../<project ID>/.tokens

token_file=${token_path_doctor}/xnat2bids_${project_id}_login.bin
# echo token file is ${token_file}
# -s flag for any file that is not empty, -r for readable, -e any type
if test -s "$token_file"; then
    echo Located token_file ${token_file}
else
    docker run \
    -it \
    -v /Users/j/MRI_DATA/nyspi/$project_id/.tokens:/.tokens \
    xnat-auth:latest \
    python3 auth.py $project_id
fi

# TODO: do we need to worry about permissions aka
# a rogue user falsely creating auths for a different project?

# TODO: determine central location of the public key and 
# how to control access to it
# ---> rn it's in the docker image ("jackgray/xnat-auth") 
# TODO: security concerns there?

# Retrieve JSESSION token before launching service,
# encrypt it, then send that token 
# python3 decrypt.py

# docker pull ${image_name}
docker run \
-it \
-e project_id=${project_id} \
--name=${service_name} \
-v ${rawdatapath_doctor}:${rawdatapath_container} \
-v ${bidsonlypath_doctor}:${bidsonlypath_container} \
-v ${workinglistpath_doctor}:${workinglistpath_container} \
-v ${token_path_doctor}:${token_path_container} \
-v ${private_path_doctor}:${private_path_container} \
${image_name};
