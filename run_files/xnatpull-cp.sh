#!/bin/env bash

# USAGE: bash xnat_pull.sh <<project ID> <exam no.>

project_id=$1
#single_exam_no=$2
log=/MRI_DATA/nyspi/${project_id}/derivatives/bidsonly/xnatpull.log

#.........................................
image_name=jackgray/dn_nifti:amd64latest
service_name=${project_id}_bidsprep_xnat_pull_${single_exam_no}
project_path=/MRI_DATA/nyspi/${project_id}
#.........................................

# UID/GID setup
# Pull group ID from project_id (working_gid)
groupinfo=$(getent group ${project_id})
while IFS=$':' read -r -a tmp ; do
working_gid="${tmp[2]}"
userinfo="${tmp[3]}"
done <<< $groupinfo
# get primary user for group
while IFS=$',' read -r -a tmp ; do
username="${tmp[0]}"
done <<< $userinfo
# Pull user ID from primary username
working_uid="$(id -u $(whoami))"
echo primary uid for ${project_id}: $working_uid
echo primary gid for ${project_id}: $working_gid

######### MOUNT PATH DEFS #################################
bidsonlypath_doctor=${project_path}/derivatives/bidsonly 
bidsonlypath_container=/bidsonly 
rawdata_path_doctor=${project_path}/rawdata 
rawdata_path_container=/rawdata 
token_path_doctor=${project_path}/.tokens
token_path_container=/tokens
private_path_doctor=/MRI_DATA/.xnat/xnat2bids_private.pem
private_path_container=/xnat/xnat2bids_private.pem
############################################################

# PREP SERVICE
docker pull ${image_name}
docker service rm ${service_name} >> /dev/null 2>&1
########################################################################

cat ${project_path}/scripts/${project_id}_working.lst | while read -r line
do
single_exam_no=(echo $line)
name=${project_id}_${single_exam_no}
echo "Starting service for ${name}" >> ${log}
# DOWNLOAD SERVICE
docker service create \
--detach \
--env project_id=${project_id} \
-e working_uid=${working_uid} \
-e working_gid=${working_gid} \
-e single_exam_no=${single_exam_no} \
--mode replicated \
--replicas 1 \
--reserve-memory 1g \
--reserve-cpu 1 \
--restart-condition none \
--name=${service_name} \
--mount type=bind,source=${rawdata_path_doctor},destination=${rawdata_path_container} \
--mount type=bind,source=${bidsonlypath_doctor},destination=${bidsonlypath_container} \
--mount type=bind,source=${token_path_doctor},destination=${token_path_container},readonly=true \
--mount type=bind,source=${private_path_doctor},destination=${private_path_container},readonly=true \
${image_name} >> ${log} 2>&1 &
#sleep 10

#while [ "$(docker service ps ${service_name} | awk '{print $6}' | sed -n '2p')"  != 'Failed' ] && [ "$(docker service ps ${service_name} | awk '{print $6}' | sed -n '2p')"  != 'Complete' ]; do


#sleep 5 &

#done

done
# docker service rm ${service_name} >> xnat2bids.log 2>&1
