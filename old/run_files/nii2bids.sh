#!/bin/env bash

# USAGE: nii2bids.sh <project ID> <exam no.>

# bash ./get_user_info.sh 


# UNIVERSAL SERVICE SETUP
#.........................................
project_id=$1
department=$2

#single_exam_no=$2
project_path=/MRI_DATA/${department}/${project_id}

# UID/GID setup for permissions handling
# Pull group ID from project_id (working_gid)
groupinfo=$(getent group ${project_id})
while IFS=$':' read -r -a tmp ; do
working_gid="${tmp[2]}"
userinfo="${tmp[3]}"
done <<< $groupinfo
username=$(whoami)
working_uid="$(id -u ${username})"
echo primary gid for ${project_id}: $working_gid
echo your uid: $working_uid

image_name=jackgray/nifti2bids:arm64latest
service_name=${project_id}_bidsprep_nii2bids_${username}
log=${project_path}/derivatives/bidsonly/xnatpull.log
#.........................................


######### MOUNT PATH DEFS #################################
bidsonlypath_doctor=${project_path}/derivatives/bidsonly 
bidsonlypath_container=/bidsonly 
rawdata_path_doctor=${project_path}/rawdata 
rawdata_path_container=/rawdata 
token_path_doctor=${project_path}/.tokens
token_path_container=/tokens
private_path_doctor=/Users/j/MRI_DATA/.xnat/xnat2bids_private.pem
private_path_container=/xnat/xnat2bids_private.pem
###########################################################

for line in `cat ${project_path}/scripts/${project_id}_working.lst`
do
single_exam_no=$line
name=${project_id}_${single_exam_no}
echo "Starting service for unzip_${name}" >> ${log}

docker service rm ${service_name} >> ${log} 2>&1
docker pull ${image_name} >> ${log} 2>&1

# NII2BIDS SERVICE
docker service create \
--detach \
-e project_id=${project_id} \
-e single_exam_no=${single_exam_no} \
-e working_gid=${working_gid} \
-e working_uid=${working_uid} \
--replicas 1 \
--reserve-memory 12GB \
--reserve-cpu 1 \
--mode replicated \
--restart-condition none \
--name=`echo ${service_name}` \
--mount type=bind,source=${rawdata_path_doctor},destination=${rawdata_path_container} \
--mount type=bind,source=${bidsonlypath_doctor},destination=${bidsonlypath_container} \
--mount type=bind,source=${token_path_doctor},destination=${token_path_container},readonly=true \
--mount type=bind,source=${private_path_doctor},destination=${private_path_container},readonly=true \
${image_name} >> ${log} 2>&1 &
sleep 5

docker service logs --details ${service_name} >> ${log} 2>&1

 sleep 60

while [ "$(docker service ps ${service_name} | awk '{print $6}' | sed -n '2p')"  != 'Failed' ] && [ "$(docker service ps ${service_name} | awk '{print $6}' | sed -n '2p')"  != 'Complete' ]; do
echo $(docker service ps ${service_name} | awk '{print $6}' | sed -n '2p')
 
done

docker service rm ${service_name} >> ${log} 2>&1


done

