#!/bin/env bash

usage()
{
  echo "usage: $0 [-i directory_for_cache  -o output_directory -l console_log_file -d 'project'   -u username    | [-h] "
  echo " Arguments specified with -d must be enclosed in single quotes''"
}


while [ "$1" != "" ]; do
    case $1 in
        -l )           shift
                       log=$1
                       ;;
        -d )           shift
                       department=$1
                       ;;
        -u )           shift
                       username=$1
                       ;;
        -p )           shift
                       project_id=$1
                       ;;
        -t )           shift
                       type=$1
                       ;;
        -e )           shift
                       exam_no=$1
                       ;;
        * )            usage
                       exit 1
    esac
    shift
done

#File= /MRI_DATA/.xnatauth/`id -un`_token.enc >> /dev/null 2>&1

#.........................................
image_name=jackgray/xnat_sync:latest
project_path=/MRI_DATA/${department}/${project_id}
# log=${project_path}/derivatives/bidsonly/xnatpull.log
username=$(whoami)
uid=$(id -u ${username})
gid=$(id -g ${project_id})

service_name=${project_id}_xnat_sync_${username}
#.........................................

######### MOUNT PATH DEFS #################################
working_list_path_doctor=${project_path}/scripts
working_list_path_container=/scripts
bidsonlypath_doctor=${project_path}/derivatives/bidsonly
bidsonlypath_container=/bidsonly
rawdata_path_doctor=${project_path}/rawdata 
rawdata_path_container=/rawdata
token_path_doctor=/MRI_DATA/.xnatauth
token_path_container=/tokens
private_path_doctor=/MRI_DATA/.xnat
private_path_container=/xnat
public_path_doctor=/MRI_DATA/.xnat
public_path_container=/public_token
############################################################

# AUTH SERVICE 
auth()
{
/usr/bin/docker run \
-it \
--rm \
--env project_id=${project_id} \
-e department=${department} \
-e uid=${uid} \
-e gid=${gid} \
-e username=${username} \
-e exam_no=${exam_no} \
-e type=${type} \
-e host=${host} \
--name=${service_name} \
--mount type=bind,source=${working_list_path_doctor},destination=${working_list_path_container} \
--mount type=bind,source=${rawdata_path_doctor},destination=${rawdata_path_container} \
--mount type=bind,source=${bidsonlypath_doctor},destination=${bidsonlypath_container} \
--mount type=bind,source=${token_path_doctor},destination=${token_path_container} \
--mount type=bind,source=${private_path_doctor},destination=${private_path_container} \
--mount type=bind,source=${public_path_doctor},destination=${public_path_container} \
jackgray/xnat_auth:latest
}

# DOWNLOAD SERVICE
download()
{
/usr/bin/docker service create \
--env project_id=${project_id} \
-e department=${department} \
-e uid=${uid} \
-e gid=${gid} \
-e username=${username} \
-e exam_no=${exam_no} \
-e action=${action} \
-e host=${host} \
--mode replicated \
--replicas 1 \
--reserve-memory 1g \
--reserve-cpu 1 \
--restart-condition none \
--mount type=bind,source=${working_list_path_doctor},destination=${working_list_path_container} \
--mount type=bind,source=${rawdata_path_doctor},destination=${rawdata_path_container} \
--mount type=bind,source=${bidsonlypath_doctor},destination=${bidsonlypath_container} \
--mount type=bind,source=${token_path_doctor},destination=${token_path_container} \
--mount type=bind,source=${private_path_doctor},destination=${private_path_container} \
--mount type=bind,source=${public_path_doctor},destination=${public_path_container} \
${image_name}
}

download