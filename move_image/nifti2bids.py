#!/pythonlibs python3

# bids src: /MRI_DATA/nyspi/<project_id>/derivativs/bidsonly/<exam_no>/scans/<series_no>/<BIDS>|<NIFTI>/<file>.json|.nii 
# bids dst: /MRI_DATA/nyspi/<project_id>/rawdata/sub-*/ses-*/anat|fmap|func/*.json|*.nii.gz

## TODO: what to do with scans.tsv & dataset_description.json

import os
import shutil
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

prepath = '/Users/j/MRI_DATA/nyspi/patensasc'
# Get list of data inside /bidsonly
bidsonly_path = '/bidsonly'
bidsonly_items = glob(bidsonly_path + '/*')
print('bidsonly:')
print(bidsonly_items)
# Fix permissions in /bidsonly
for item in bidsonly_items:
    print("/bidsonly: Fixing permissions on folder " + item)
    os.chown(item, working_uid, working_gid)
# Get list of subjects inside /rawdata 
rawdata_path = '/rawdata'
rawdata_items = glob(rawdata_path + '/*')
print('rawdata items:')
print(rawdata_items)
# Fix permissions in /rawdata
for item in rawdata_items:
    print("/rawdata: Fixing permissions on folder " + item)
    os.chown(item, working_uid, working_gid)
# Remove these after adding perms fix to download script.
# so that we only edit perms on files affected by the script

zips = []


for exam in bidsonly_items: 
    print(exam)

    # Create queue by exam number for zipfiles (remove .zip extension)
    if '.zip' in exam:
        #  with ZipFile(exam, 'r') as zip:
            # zip.printdir()
        zipfile = exam + '.zip'
        try:
            shutil.unpack_archive(zipfile, '/bidsonly')
            print("Done.")
            print("Fixing perms on " + zipfile + '.')
            os.chown(zipfile, working_uid, working_gid)
            try:
                print("Removing .zip file...")
                os.rmdir(zipfile)
                print("Removed zip file.")
            except:
                print("unable to remove directory")
        except:
            print("could not unzip. disk quota error")
    # only remove zip file after sucessful transfer    
    


    # If there are letters then this is not an exam folder
    elif exam.isalpha():
        print(exam + " doesn't seem to be an exam. Skipping.")   
        
    # If there are only numbers this is probably an exam folder
    elif exam.isnumeric and 'zip' not in exam:
        print(exam + " looks like data that needs sorting")

        files2move = glob(exam + '/SCANS/*/*/*')

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
            
        
            # Session dir
            sesname = filename.split('_')[1]
            ses_path = sub_path + '/' + sesname 
            if not os.path.isdir(ses_path):
                print('Creating directory ' + ses_path)
                os.mkdir(ses_path)
            
        # Sort sequence type into /anat, /func, /fmap
            # make folders if they don't exist
            anat_path = ses_path + '/anat'
            if not os.path.isdir(anat_path):
                print('Creating directory ' + anat_path)
                os.mkdir(anat_path)

            fmap_path = ses_path + '/fmap'
            if not os.path.isdir(fmap_path):
                print('Creating directory ' + fmap_path)
                os.mkdir(fmap_path)
            
            func_path = ses_path + '/func'
            if not os.path.isdir(func_path):
                print('Creating directory ' + func_path)
                os.mkdir(func_path)
            
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
                sort_path = ses_path + '/sort'
                if not os.path.isdir(sort_path):
                    print('Creating directory ' + sort_path + ' to catch else cases.')
                    os.mkdir(sort_path)
                    shutil.move(file, sort_path)
            
            print("\nSending: " + filename + "\nto: " + target_path)
            try:
                shutil.move(file, target_path)
                print("\Yay! sent: " + filename + "\nto: " + target_path)

            except:
                print("Error moving file. Maybe it's already there?")

            os.chown(target_path, working_uid, working_gid)