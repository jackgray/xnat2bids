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
        -a )           shift
                       action=$1
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

# /usr/bin/docker service create  --replicas 1 --reserve-cpu 8 --reserve-memory 16g --mode replicated --restart-condition none --name=nyspi_bids_setup_`id -un` --mount type=bind,source=$indir,destination=/input  --mount type=bind,source=$outdir,destination=/output --mount type=bind,source=/MRI_DATA/freesurferlicense.txt,destination=/opt/freesurfer/license.txt,readonly=true --mount type=bind,source=$code,destination=/.token --mount type=bind,source=$code2,destination=/.private_key.pem --mount type=bind,source=/MRI_DATA/download.sh,destination=/usr/local/bin/download.sh  --mount type=bind,source=/MRI_DATA/${dept}/$proid/scripts/${proid}_working.lst,destination=/working.lst radiologicsit/download-bids-setup:1.1 download.sh  -o 'https://xnat.nyspi.org/' -u $user  -i $proid  -c/input -b/output  > $log 2>&1 &


# Pass arguments as env vars from service launch script
# project_id = environ['project_id']
# exam_no = str(environ['single_exam_no'])
# username = environ['username']
# uid = environ['uid']
# gid = environ['gid'] 
# jsession_token = environ['jsession_token']

# bids_flag = environ['dl_bids']
# nm_flag = environ['dl_nm']


#single_exam_no=$2

#.........................................
image_name=jackgray/xnat_sync:latest
project_path=/MRI_DATA/${department}/${project_id}
echo $project_path
# log=${project_path}/derivatives/bidsonly/xnatpull.log
uid=1000
gid=1000
# uid=$(id -u)
# gid=$(id -g ${project_id})
username=$(whoami)
username=grayjoh
service_name=${project_id}_xnat_sync
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
############################################################

# DOWNLOAD SERVICE
/usr/bin/docker service create \
-t \
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
--name=${service_name} \
--mount type=bind,source=${working_list_path_doctor},destination=${working_list_path_container} \
--mount type=bind,source=${rawdata_path_doctor},destination=${rawdata_path_container} \
--mount type=bind,source=${bidsonlypath_doctor},destination=${bidsonlypath_container} \
--mount type=bind,source=${token_path_doctor},destination=${token_path_container} \
--mount type=bind,source=${private_path_doctor},destination=${private_path_container} \
${image_name}