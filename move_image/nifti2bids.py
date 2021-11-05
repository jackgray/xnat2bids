#!/pythonlibs python3

# bids src: /MRI_DATA/nyspi/<project_id>/derivativs/bidsonly/<exam_no>/scans/<series_no>/<BIDS>|<NIFTI>/<file>.json|.nii 
# bids dst: /MRI_DATA/nyspi/<project_id>/rawdata/sub-*/ses-*/anat|fmap|func/*.json|*.nii.gz

## TODO: what to do with scans.tsv & dataset_description.json

import os, shutil, sys, stat
from glob import glob
from os import environ as env
from zipfile import ZipFile

# project_id = env['project_id']
# try:
#     exam_no = env['exam_no']
# except:
#     print('no exam number provided. Looking for any and all data in /bidsonly...')
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

rawdata_path = '/rawdata'
rawdata_items = glob(rawdata_path + '/*')
# Collect filenames for contents of zipfile
with ZipFile(zipfile_path, 'r') as zip:
    zipped_files = zip.namelist()      
# Use thoes filenames in a loop to extract them file by file
for file in zipped_files:
    print("Unzipping " + file + '...')
    try:
        with ZipFile(zipfile_path, 'r') as zip:
            zip.extract(file, bidsonly_path)
    except:
        print("Error extracting " + file)
        continue
# Correct permissions for downloaded zipfile
os.chown(exam_path, working_uid, working_gid)
os.chmod(exam_path, stat.S_IRWXG)
os.chown(zipfile_path, working_uid, working_gid)
os.chmod(zipfile_path, stat.S_IRWXG)
try:
    print("Removing .zip file...")
    os.remove(zipfile_path)
    print("Removed zip file.")
except:
    print("unable to remove zipfile " + zipfile_path)
print("Done.")

# Extract paths to every file in exam path as a list
files2move = glob(exam_path + '/SCANS/*/*/*')

# Extract context from filename
for file in files2move:
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
        os.chown(sub_path, working_uid, working_gid)

    # Session dir
    sesname = filename.split('_')[1]
    ses_path = sub_path + '/' + sesname 
    if not os.path.isdir(ses_path):
        print('Creating directory ' + ses_path)
        os.mkdir(ses_path)
        os.chown(ses_path, working_uid, working_gid)
    
    # Sort sequence type into /anat, /func, /fmap
    # make folders if they don't exist
    anat_path = ses_path + '/anat'
    if not os.path.isdir(anat_path):
        print('Creating directory ' + anat_path)
        os.mkdir(anat_path)
        os.chown(anat_path, working_uid, working_gid)
        os.chmod(anat_path, stat.S_IRWXG)
    fmap_path = ses_path + '/fmap'
    if not os.path.isdir(fmap_path):
        print('Creating directory ' + fmap_path)
        os.mkdir(fmap_path)
        os.chown(fmap_path, working_uid, working_gid)
        os.chmod(anat_path, stat.S_IRWXG)
    func_path = ses_path + '/func'
    if not os.path.isdir(func_path):
        print('Creating directory ' + func_path)
        os.mkdir(func_path)
        os.chown(func_path, working_uid, working_gid)
        os.chmod(anat_path, stat.S_IRWXG)

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
            os.chmod(sort_path, stat.S_IRWXG)
        target_path = sort_path
    # Move the file 
    print("\nSending: " + filename + "\nto: " + target_path)
    try:
        os.chown(file, working_uid, working_gid)
        shutil.move(file, target_path)
        print("\Yay! sent: " + filename + "\nto: " + target_path)

    except:
        print("Error moving file. Maybe it's already there?")

    os.chown(target_path, working_uid, working_gid)
    os.chmod(anat_path, stat.S_IRWXG)
    os.remove(exam_path)