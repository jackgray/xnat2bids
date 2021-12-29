#!/pythonlibs python3

# bids src: /MRI_DATA/nyspi/<project_id>/derivativs/bidsonly/<exam_no>/scans/<series_no>/<BIDS>|<NIFTI>/<file>.json|.nii 
# bids dst: /MRI_DATA/nyspi/<project_id>/rawdata/sub-*/ses-*/anat|fmap|func/*.json|*.nii.gz

## TODO: what to do with scans.tsv & dataset_description.json

import os, shutil, sys, stat
from glob import glob
from os import environ as env
from zipfile import ZipFile

working_uid = int(env['working_uid'])
working_gid = int(env['working_gid'])
exam = str(env['single_exam_no'])

zips = []
count = 0

    # prepath = '/Users/j/MRI_DATA/nyspi/patensasc'
    # Get list of data inside /bidsonly
bidsonly_path = '/bidsonly'
exam_path = bidsonly_path + '/' + exam
zipfile_path = exam_path + '.zip'

bidsonly_items = glob(bidsonly_path + '/*')

# SET PERMISSIONS
def set_permissions(path):
    os.chown(path, working_uid, working_gid)
    os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IRWXG | stat.S_IRWXU )

for i in bidsonly_items:
    set_permissions(i)

rawdata_path = '/rawdata'
rawdata_items = glob(rawdata_path + '/*')
# Collect filenames for contents of zipfile
with ZipFile(zipfile_path, 'r') as zip:
    zipped_files = zip.namelist()      
# Use thoes filenames in a loop to extract them file by file
for file in zipped_files:
    src_path = bidsonly_path + '/' + file
    print("\nUnzipping " + file + '...')
    try:
        with ZipFile(zipfile_path, 'r') as zip:
            zip.extract(file, bidsonly_path)
    except:
        print("\nError extracting " + file)

    set_permissions(src_path)

    filename = file.split('/')[-1]
    print('file: ' + str(filename))

    # Create destination folders
    # Subject dir
    subname = filename.split('_')[0]
    print("subname: " + str(subname))
    sub_path = rawdata_path + '/' + subname
    if not os.path.isdir(sub_path):
        print('Creating directory ' + str(sub_path))
        os.mkdir(sub_path)
        set_permissions(sub_path)


    # Session dir
    sesname = filename.split('_')[1]
    ses_path = sub_path + '/' + sesname 
    if not os.path.isdir(ses_path):
        print('Creating directory ' + ses_path)
        os.mkdir(ses_path)
        set_permissions(ses_path)

    
    # Sort sequence type into /anat, /func, /fmap
    # make folders if they don't exist
    anat_path = ses_path + '/anat'
    if not os.path.isdir(anat_path):
        print('Creating directory ' + anat_path)
        os.mkdir(anat_path)
        set_permissions(anat_path)
    fmap_path = ses_path + '/fmap'
    if not os.path.isdir(fmap_path):
        print('Creating directory ' + fmap_path)
        os.mkdir(fmap_path)
        set_permissions(fmap_path)
    func_path = ses_path + '/func'
    if not os.path.isdir(func_path):
        print('Creating directory ' + func_path)
        os.mkdir(func_path)
        set_permissions(func_path)


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
        print("\n\n\n                             ATTENTION!!!!! \n\n\nthe following files will be moved to a directory called \'sort\' because they were not caught by this program's matching criteria.")
        print(filename)
        print("Oops! This file wasn't caught by my filter. I'm going to put it in this folder called 'sort', and you can decide what to do with it. If this is a re-ocurring issue, reach out to a member of the MRI computing department.")
        sort_path = ses_path + '/sort'
        # Sort them in a directory called /sort
        if not os.path.isdir(sort_path):
            print('Creating directory ' + sort_path + ' to catch else cases.')
            os.mkdir(sort_path)
            set_permissions(sort_path)

        target_path = sort_path
    # Move the file 
    print("\nSending: " + filename + "\nto: " + target_path)
    try:
        set_permissions(src_path)
        shutil.move(src_path, target_path)
        filepath = target_path + '/' + filename
        set_permissions(filepath)
        print("\Yay! sent: " + filename + "\nto: " + target_path)

    except:
        print("Error moving file. Maybe it's already there?")

# Delete the zip file
set_permissions(zipfile_path)
try:
    print("Removing .zip file...")
    os.remove(zipfile_path)
    print("Removed zip file.")
except:
    print("unable to remove zipfile " + zipfile_path)
print("Done.")



# This folder should now be empty (sanity check)
files_remaining = glob(exam_path + '/SCANS/*/*/*')
print("This array should be empty. Whatever is here was not moved out of /bidsonly")
print(files_remaining)


# Delete old directory in /bidsonly
set_permissions(exam_path)

def remove_empty_folders(path_abs):
    walk = list(os.walk(path_abs))
    for path, _, _ in walk[::-1]:
        if len(os.listdir(path)) == 0:
            set_permissions(path)
            os.remove(path)

try:
    remove_empty_folders(exam_path)
except:
    print("Can't remove empty folders or figure out why.. It's not hard, I know...")

try:
    os.rmdir(exam_path)
    print("Woot!! os.rmdir worked")
except:
    print("Tried again using os.rmdir() but failed miserably.")

try:
    shutil.rmtree(exam_path, ignore_errors=False, onerror=None)
    print("Whaaaat. shutil.rmtree() worked! sweet!")
except:
    print("Tried again using shutil.rmtree() and failed.")