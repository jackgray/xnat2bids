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

image_name=xnat2bids
service_name=xnat2bids_${project_id_}$(date)

# docker pull jackgray/xnat2bids

docker service create\
    --replicas 1\
    --reserve-cpu 8\
    --reserve-memory 16g\
    --mode replicated\
    --restart-condition none\
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
    ${image_name}\
    python3 dn_nifti.py ${project_id};\
    python3 nifti2bids.py ${project_id}

# TODO: configure options to run all either, or or both scripts