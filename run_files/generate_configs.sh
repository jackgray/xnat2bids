#!/bin/env bash

# Usage: bash generate_configs.sh <project ID>

# This script will use your encrypted user/pass token in <project ID>/.tokens 
# If you have trouble running this, try running the auth.sh script

# This will use a web crawler to log in to your xnat account 
# and scrape the text from the sequence list ('/data/archive/projects/' + project_id + '/experiments?xsiType=xnat:mrSessionData&format=csv&columns=ID,label,xnat:subjectData/label')


# UNIVERSAL SERVICE SETUP
#.........................................
project_id=$1
# single_exam_no=$2
project_path=/Users/j/MRI_DATA/nyspi/${project_id}
image_name=jackgray/bids_configurator:arm64latest
service_name=${project_id}_bidsprep_configurator_${single_exam_no}
#.........................................

# UID/GID setup
# Pull group ID from project_id (working_gid)
# groupinfo=$(getent group ${project_id})
# while IFS=$':' read -r -a tmp ; do
# working_gid="${tmp[2]}"
# userinfo="${tmp[3]}"
# done <<< $groupinfo
# # get primary user for group
# while IFS=$',' read -r -a tmp ; do
# username="${tmp[0]}"
# done <<< $userinfo
# # Pull user ID from primary username
# working_uid="$(id -u $(whoami))"
# echo primary uid for ${project_id}: $working_uid
# echo primary gid for ${project_id}: $working_gid

######### MOUNT PATH DEFS #################################
bidsconfigpath_doctor=${project_path}/ 
bidsconfigpath_container=/bidsconfig 
token_path_doctor=${project_path}/.tokens
token_path_container=/tokens
private_path_doctor=${project_path}/.tokens/xnat2bids_private.pem
private_path_container=/xnat/xnat2bids_private.pem
###########################################################

# docker service rm ${service_name}
docker pull ${image_name}

# BIDSCONFIG SERVICE
docker run \
-it \
-e project_id=${project_id} \
--mount type=bind,source=${bidsconfigpath_doctor},destination=${bidsconfigpath_container} \
--mount type=bind,source=${token_path_doctor},destination=${token_path_container},readonly=true \
--mount type=bind,source=${private_path_doctor},destination=${private_path_container},readonly=true \
${image_name};

# docker service rm $service_name