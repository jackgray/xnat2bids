#!/bin/bash

# Usage: bash sub-xnat2bids.sh <project ID>

project_id=$1
project_path=/MRI_DATA/nyspi/${project_id}
bidsonlypath_doctor=${project_path}/derivatives/bidsonly 
rawdata_path_doctor=${project_path}/rawdata 
workinglistpath_doctor=${project_path}/scripts/${project_id}_working.lst
bidsonlypath_container=${project_path}/derivatives/bidsonly 
rawdata_path_container=${project_path}/rawdata 
workinglistpath_container=${project_path}/scripts/${project_id}_working.lst
token_path_doctor=${project_path}/.tokens
token_path_container=${project_path}/.tokens
image_name=xnat2bids
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
    python3 ./app/auth.py
fi

# TODO: do we need to worry about permissions aka
# a rogue user falsely creating auths for a different project?

# TODO: determine central location of the public key and 
# how to control access to it

# Retrieve JSESSION token before launching service,
# encrypt it, then send that token 
python3 decrypt.py

# docker pull jackgray/xnat2bids
docker run \
    --name=${service_name}\
    --mount type=bind,\
    source=${rawdatapath_doctor},\
    destination=${rawdatapath_container}\
    --mount type=bind,\
    source=${bidsonlypath_doctor},\
    destination=${bidsonlypath_container}\
    --mount type=bind,\
    source=${workinglistpath_doctor},\
    destination=${workinglistpath_container}\
    --mount type=bind,\
    source=${token_path_doctor},\
    destination=${token_path_container}\
    ${image_name}\
    python3 xnat2bids.py ${project_id};\
