#!/bin/env bash

# Usage: bash sub-xnat2bids.sh <project ID>
project_id=$1
single_exam_no=${2:-null}
project_path=/MRI_DATA/nyspi/${project_id}

token_path_doctor=${project_path}/.tokens

auth_image=jackgray/xnat_auth:amd64
auth_service_name=xnat_auth_${project_id}

xnat2bids_image=jackgray/xnat2bids:amd64
xnat2bids_service_name=xnat2bids_${project_id}
docker service rm ${auth_service_name}
docker service rm ${xnat2bids_service_name}
docker pull ${xnat2bids_image}

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
    docker pull ${auth_image}
    # touch token_file
    docker run \
    -it \
    -e project_id=${project_id} \
    --name=${auth_service_name} \
    --mount type=bind,source=${project_path}/.tokens,destination=/tokens,readonly=false \
     ${auth_image};
fi

# TODO: consider--do we need to worry about permissions aka
# a rogue user falsely creating auths for a different project?

# TODO: determine central location of the public key and 
# how to control access to it
# ---> rn it's in the docker image ("jackgray/xnat-auth") 
# TODO: consider--security concerns there?

# Consideration: retrieve JSESSION token before launching service,
# encrypt it, then send that token -- update: doesn't seem to be necessary

bidsonlypath_doctor=${project_path}/derivatives/bidsonly 
bidsonlypath_container=/derivatives/bidsonly 
rawdata_path_doctor=${project_path}/rawdata 
rawdata_path_container=/rawdata 
workinglistpath_doctor=${project_path}/scripts/${project_id}_working.lst
workinglistpath_container=/scripts/${project_id}_working.lst
token_path_doctor=${project_path}/.tokens
token_path_container=/tokens
private_path_doctor=/MRI_DATA/.xnat/xnat2bids_private.pem
private_path_container=/xnat/xnat2bids_private.pem
# ^ btwn the RSA import func and distroless something doesn't like .folder names 
# (does not seem to be an issue with bloatier official python3 image above)

docker service create \
--replicas 1 \
--reserve-memory 4g \
--reserve-cpu 4 \
--mode replicated \
-e project_id=${project_id} \
-e single_exam_no=${single_exam_no}
--name=${xnat2bids_service_name} \
--mount type=bind,source=${rawdata_path_doctor},destination=${rawdata_path_container} \
--mount type=bind,source=${bidsonlypath_doctor},destination=${bidsonlypath_container} \
--mount type=bind,source=${workinglistpath_doctor},destination=${workinglistpath_container},readonly=true \
--mount type=bind,source=${token_path_doctor},destination=${token_path_container},readonly=true \
--mount type=bind,source=${private_path_doctor},destination=${private_path_container},readonly=true \
${xnat2bids_image};
