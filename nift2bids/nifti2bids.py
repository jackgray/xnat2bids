#!/usr/bin/python3

# usage: python3 nifti2bids.py <working-list-path>

# bids src: /MRI_DATA/nyspi/<project_id>/derivativs/bidsonly/<exam_no>/scans/<series_no>/<BIDS>|<NIFTI>/<file>.json|.nii 
# bids dst: /MRI_DATA/nyspi/<project_id>/rawdata/sub-*/ses-*/anat|fmap|func/*.json|*.nii.gz

## TODO: what to do with scans.tsv & dataset_description.json

import argparse
import os
import shutil
import glob
# import unzip

# Take args
parser = argparse.ArgumentParser(description='Move niftis to make them less annoying')
parser.add_argument("project_id")
# parser.add_argument("project_id")
# parser.add_argument("exam_no")
args = parser.parse_args()

project_id = args.project_id
project_path = '/Users/j/Documents/Code/NYSPI/nifti2bids/dn_nifti/MRI_DATA/nyspi/' + project_id
working_list_file = project_id + '_working.lst'
working_list_path = project_path + '/scripts/' + working_list_file
with open(working_list_path) as f:
    jobs = f.readlines()

active_job_no = 0
total_jobs=len(jobs)

# Run operation for every exam in working list
for job in jobs:
    active_job_no+=1
    print("\nRunning job " + str(active_job_no) + ' of ' + str(total_jobs))

    args = job.split('\t')
    arg_no = 0
    print('Using the following input arguments: ')
    for arg in args:
        arg_no+=1
        print('arg' + str(arg_no) + ': ' + arg)
   
    # working.lst format: <subj_id> '\t' <project_id> '\t' <exam_no> '\t' XNATnyspi20_E00253
    exam_no = args[2]
    project_id = args[1]
    subj_id = args[0] 

    # Define paths
    # dn_nifti --> /derivatives/bidsonly
    bidsfiles_src = './dn_nifti/MRI_DATA/nyspi/' + project_id + '/derivatives/bidsonly/' + exam_no + '/'
    
    # Use glob to pull paths to every file
    file_dirs = glob.glob(bidsfiles_src + 'SCANS/*/*/*')
    rawdata_path = '/Users/j/Documents/Code/nyspi/nifti2bids/dn_nifti/MRI_DATA/nyspi/' + project_id + '/rawdata/'
    
    # print("\nThis script will attempt to organize the following files: \n")
    # for file_dir in file_dirs:
    #     print(file_dir)

    for file in file_dirs:
        
        filename = file.split('/')[11]
        print('FILENAME= ' + filename)

    # Create destination folders

        # Subject dir
        subname = filename.split('_')[0]
        sub_path = rawdata_path + subname
        if not os.path.isdir(sub_path):
            print('Creating directory ' + sub_path)
            os.mkdir(sub_path)
        else: 
            print("\n" + sub_path + ' already exists.')

        # Session dir
        sesname = filename.split('_')[1]
        ses_path = sub_path + '/' + sesname 
        if not os.path.isdir(ses_path):
            print('Creating directory ' + ses_path)
            os.mkdir(ses_path)
        else:
            print(ses_path + ' already exists.')

    # Sort sequence type into /anat, /func, /fmap

        # make folders if they don't exist
        anat_path = ses_path + '/anat'
        if not os.path.isdir(anat_path):
            print('Creating directory ' + anat_path)
            os.mkdir(anat_path)
        else:
            print(anat_path + ' already exists.')

        fmap_path = ses_path + '/fmap'
        if not os.path.isdir(fmap_path):
            print('Creating directory ' + fmap_path)
            os.mkdir(fmap_path)
        else:
            print(fmap_path + ' already exists.')

        func_path = ses_path + '/func'
        if not os.path.isdir(func_path):
            print('Creating directory ' + func_path)
            os.mkdir(func_path)
        else:
            print(func_path + ' already exists.')
        
        sequence_name = filename.split('_')[2]  # i.e. 'run-01'
        sequence_type = filename.split('.')[0].split('_')[-1]   # i.e. 'epi', 'T2w', 'T1w'
        
        # Move fmaps
        if 'dir-' in sequence_name:
            target_path = fmap_path
        
        # Move anats
        elif 'w' in sequence_type:
            target_path = anat_path
        
        # Move funcs
        elif 'bold' in sequence_type:
            target_path = func_path
        
        # Notify if files weren't sorted properly
        else:
            print("\n\n\n                             ATTENTION!!!!! \n\n\nthe following files will be moved to a directory called \'sort\' because they were not caught by this program's matching criteria.")
            print(filename)
            sort_path = ses_path + '/sort'
            if not os.path.isdir(sort_path):
                print('Creating directory ' + sort_path + ' to catch else cases.')
                os.mkdir(sort_path)
                shutil.move(file, sort_path)
        
        print("\nSending: " + filename + "\nto: " + target_path)
        shutil.move(file, target_path)
