#!/pythonlibs python3

# bids src: /MRI_DATA/nyspi/<project_id>/derivativs/bidsonly/<exam_no>/scans/<series_no>/<BIDS>|<NIFTI>/<file>.json|.nii 
# bids dst: /MRI_DATA/nyspi/<project_id>/rawdata/sub-*/ses-*/anat|fmap|func/*.json|*.nii.gz

## TODO: what to do with scans.tsv & dataset_description.json

import os
import shutil
import glob
from datetime import datetime as dt

from os import environ as env
# project_id = env['project_id']
# exam_no = env['exam_no']

def move2bids(exam_no):
    # Define paths
    bidsfiles_src = '/derivatives/bidsonly/' + exam_no 
    # Use glob to pull paths to every file
    file_dirs = glob.glob(bidsfiles_src + '/SCANS/*/*/*')
    # To avoid permissions issues, organize files into a directory 
    # that is not bind-mounted with the host, then move the entire folders
    rawdata_path = '/pre_rawdata'
    
    print("\nThis script will attempt to organize the following files: \n")
    for file_dir in file_dirs:
        print(file_dir)

    for file in file_dirs:
        filename = file.split('/')[-1]
        print('Moving file: ' + filename)

        # Create destination folders
        # Subject dir
        subname = filename.split('_')[0]
        sub_path = rawdata_path + '/' + subname
        if not os.path.isdir(sub_path):
            print('Creating directory ' + sub_path)
            os.mkdir(sub_path)
        else: 
            print("\n" + sub_path + ' already exists. Checking for new sessions...')

        # Session dir
        sesname = filename.split('_')[1]
        ses_path = sub_path + '/' + sesname 
        if not os.path.isdir(ses_path):
            print('Creating directory ' + ses_path)
            os.mkdir(ses_path)
        else:
            print('Located session' + ses_path + ". Making sure you have the right folders here. If you don't I will fix that :)")
        # Sort sequence type into /anat, /func, /fmap
        # Make folders if they don't exist
        anat_path = ses_path + '/anat'
        if not os.path.isdir(anat_path):
            print('Creating directory ' + anat_path)
            os.mkdir(anat_path)
        else:
            print("Found " + anat_path + '. Check.')

        fmap_path = ses_path + '/fmap'
        if not os.path.isdir(fmap_path):
            print('Creating directory ' + fmap_path)
            os.mkdir(fmap_path)
        else:
            print('Found ' + fmap_path + '. Check.')

        func_path = ses_path + '/func'
        if not os.path.isdir(func_path):
            print('Creating directory ' + func_path)
            os.mkdir(func_path)
        else:
            print("Found " + func_path + ". Check! \n Ok, now we'll set the target path of " + file)
        
        sequence_name = filename.split('_')[2]  # i.e. 'run-01'
        print("sequence name: " + sequence_name)
        sequence_type = filename.split('.')[0].split('_')[-1]   # i.e. 'epi', 'T2w', 'T1w'
        print("sequence_type: " + sequence_type)

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
            print("\n\n\n             ATTENTION  \
                \n\n\nThe following file will be moved to a directory called \'sort\' because they were not caught by this program's matching criteria.")
            print(filename)
            print("\nAdding filename to log so I can catch it next time :)")
            sort_path = ses_path + '/sort'
            if not os.path.isdir(sort_path):
                print('Creating directory ' + sort_path)
                os.mkdir(sort_path)
                shutil.move(file, sort_path)
        
        print("\nSending: " + filename + "\nto: " + target_path)
        shutil.move(file, target_path)

    # downloading individual sessions to pre-existing subjects
    # will overwrite the data this way.
    # If the full subject folder gets added to the bind-mounted 
    # raw data folder, it will replace any subject folder that
    # already exists. The is a working solution while we troubleshoot
    # uid/gid matching issues inside a root-only distroless container
    truedest = '/rawdata' + target_path.split('/')[1:].join('/')
    temp_dest = truedest + dt()  # Datetime appended to end of subject name
    print("Could not resolve permissions to check if subject folder already exists on the server. To avoid \
        potentially overwriting any data, the subject folder will have the date added to it. \nTo merge the \
            recent session into a prexisting subject folder, run mv /MRI_DATA/nyspi/" + project_id + temp_dest + ' /MRI_DATA/nyspi/' + project_id + truedest)

    shutil.move(sub_path, temp_dest)

if __name__ == '__main__':
    move2bids(exam_no)
