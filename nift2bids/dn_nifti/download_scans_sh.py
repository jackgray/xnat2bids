#!/usr/bin/python3
# contact john.gray@nyspi.columbia.edu for questions

     
# USAGE: python3 dn_nifti.py /path/to/working.lst 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Runs download_scans_jack.sh with working.lst path as argument
# <project_id>_working.lst located in /MRI_DATA/nyspi/<project_id>/scripts

import shutil
import os 



#............................................................
#   working.lst ARGUMENT PARSER
#   copy & paste anywhere for working.lst parsing in python
#............................................................
import argparse

parser = argparse.ArgumentParser(description='Download output of dcm2bids from XNAT.')
parser.add_argument("working_list_path")
args = parser.parse_args()

working_list_path = args.working_list_path
with open(working_list_path) as f:
    jobs = f.readlines()

active_job_no = 0
total_jobs=len(jobs)
print("\n" + str(total_jobs) + ' jobs found in working list.')
# Run operation for every exam in working list
for job in jobs:
    active_job_no+=1
    print("\nRunning job " + str(active_job_no) + ' of ' + str(total_jobs))

    args = job.split('\t')
    arg_no = 0
    print('using the following input arguments: ', *args)
   
    # working.lst format: <subj_id> '\t' <project_id> '\t' <exam_no> '\t' XNATnyspi20_E00253
    exam_no = args[2]
    project_id = args[1]
    subj_id = args[0] 
    accession_no = args[3]
#............................................................
#   END COPY & PASTE (continue indent for loop above)
#............................................................
    
    xnat_url = 'https://xnat.nyspi.org'
    output_dir = '/Users/j/MRI_DATA/nyspi/' + project_id + '/derivatives/bidsonly'

    print("Running download_scans_jack.sh and saving .json, nifti, and mriqc files to ", output_dir)

    resource_name = "BIDS,NIFTI,MRIQC"

def login():
    import getpass
    print("Log in to XNAT to download data: ")
    xnat_username = input('Username: ')
    xnat_password = getpass.getpass()
    jsession_url=host + '/data/JSESSION'
    if jsession_id: 
        shutil('curl --cookie JSESSIONID=jession_id " -X DELETE >/dev/null 2>&1')
    
    else:
        jsession_id=`curl -u $uname:$pass jsession_url -X POST 2>/dev/null`

login