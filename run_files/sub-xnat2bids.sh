#!/bin/env bash

# Usage: bash sub-xnat2bids.sh <project ID>

project_id=$1
single_exam_no=$2
xnat2bids_queue=/MRI_DATA/nyspi/${project_id}/scripts/xnat2bids_queue.txt

# AUTHORIZATION (only needs to run once per project)
bash auth.sh $project_id

queue_items=$(cat $xnat2bids_queue)
for exam in $queue_items
# GET 👏 THE 👏 DATA 👏
do
    # DOWNLOAD NIFTI AND JSON
    # Dedicated service for each exam on the list
    bash dn_nifti.sh $project_id $exam
    sleep 90s
    # ORGANIZE INTO /RAWDATA BY BIDS
    # Dedicated service for each exam on the list
    bash nifti2bids.sh $project_id
done


