#!/bin/bash

# USAGE: enter path to <project_id>_working.lst

# the following input args are defined by 
# <project_id>_working.lst located in /MRI_DATA/nyspi/<project_id>/scripts

project_id=$1
exam_no=$2

working_list_path=$1
args=$(cat $working_list_path)
total_jobs=$(echo -n $"args" | grep -c '^')
active_job_number=0
# read -p 'XNAT Username: ' xnat_username
# read -sp 'Password: ' xnat_password

 active_job_number+=1
echo "Running job $active_job_number of $total_jobs"

output_dir=/Users/j/MRI_DATA/nyspi/$project_id/derivatives/bidsonly

echo ""
echo "Running download_scans with arguments: \"$project_id\""
echo "Exam number: $exam_no"
echo "Saving files to $output_dir"
echo ""
echo ""
    # this should be fixed
resource_name=BIDS,NIFTI,MRIQC
echo "Downloading the following resources from XNAT: "
echo $resource_name
echo 
echo
# remove " -s $exam_no " for production use as script will skip existing sessions, 
# making it suitable for chron task syncing


bash download_scans_jack.sh \
    -i $project_id \
    -s $exam_no \
    -d $output_dir \
    -f $resource_name \
    -o https://xnat.nyspi.org 
    # -u $xnat_username \
    # -p $xnat_password


