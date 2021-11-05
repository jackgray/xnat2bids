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

zips = []
count = 0
# Run twice to catch folders that were unzipped in the first loop
while count < 2:
    print("count: " + str(count))
    count+=1
    # prepath = '/Users/j/MRI_DATA/nyspi/patensasc'
    # Get list of data inside /bidsonly
    bidsonly_path = '/bidsonly'
    bidsonly_items = glob(bidsonly_path + '/*')
    print('bidsonly:')
    print(bidsonly_items)
    # Fix permissions in /bidsonly
    # for item in bidsonly_items:
    #     print("/bidsonly: Fixing permissions on folder " + item)
    #     os.chown(item, working_uid, working_gid)
    # Get list of subjects inside /rawdata 
    rawdata_path = '/rawdata'
    rawdata_items = glob(rawdata_path + '/*')
    print('rawdata items:')
    print(rawdata_items)
    # Fix permissions in /rawdata
    # for item in rawdata_items:
    #     print("/rawdata: Fixing permissions on folder " + item)
    #     os.chown(item, working_uid, working_gid)
    # Remove these after adding perms fix to download script.
    # so that we only edit perms on files affected by the script


    for bidsonly_item_path in bidsonly_items: 
        print(bidsonly_item_path)

        # Create queue by exam number for zipfiles (remove .zip extension)
        if '.zip' in bidsonly_item_path:
            zipfile = bidsonly_item_path
            exam = bidsonly_item_path.split('.')[0]
            print("exammmm: " + exam)
            #  with ZipFile(bidsonly_item_path, 'r') as zip:
                # zip.printdir()
            zipfile = exam + '.zip'
            try:
                # Collect list of zipfile contents to extract each file
                # one at a time
                with ZipFile(zipfile, 'r') as zip:
                    zipped_files = zip.namelist()
            except:
                print("Error reading file list of zip.")  
                continue
            # Extract file by file
            for file in zipped_files:
                print("Gonna try to unzip this file: " + file)
                try:
                    with ZipFile(zipfile, 'r') as zip:
                        zip.extract(file, bidsonly_path)
                    # only remove zip file after sucessful transfer
                except:
                    print("Error extracting " + file)
                    continue
                # folder_tree = glob(exam + '/*/*/*')
                # print(*folder_tree)
            # Correct permissions for downloaded zipfile
            os.chown(exam, working_uid, working_gid)
            try:
                print("Removing .zip file...")
                shutil.rmtree(zipfile)
                print("Removed zip file.")
            except:
                print("unable to remove zipfile " + zipfile)
                continue

            print("Done.")
            print("Fixing perms on " + exam + '.')
            os.chown(exam, working_uid, working_gid)
                   


        # If there are letters then this is not an exam folder
        if bidsonly_item_path.isalpha():
            print(bidsonly_item_path + " doesn't seem to be an exam. Skipping.")   
            
        # If there are only numbers this is probably an exam folder
        if bidsonly_item_path.isnumeric() and '.zip' not in bidsonly_item_path:
            print(bidsonly_item_path + " looks like data that needs sorting")

            files2move = glob(bidsonly_item_path + '/SCANS/*/*/*')

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
                    os.chown(ses_path, working_uid, working_gid)
                
            # Sort sequence type into /anat, /func, /fmap
                # make folders if they don't exist
                anat_path = ses_path + '/anat'
                if not os.path.isdir(anat_path):
                    print('Creating directory ' + anat_path)
                    os.mkdir(anat_path)
                    os.chown(anat_path, working_uid, working_gid)


                fmap_path = ses_path + '/fmap'
                if not os.path.isdir(fmap_path):
                    print('Creating directory ' + fmap_path)
                    os.mkdir(fmap_path)
                    os.chown(fmap_path, working_uid, working_gid)

                func_path = ses_path + '/func'
                if not os.path.isdir(func_path):
                    print('Creating directory ' + func_path)
                    os.mkdir(func_path)
                    os.chown(func_path, working_uid, working_gid)

                
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
                    os.chown(file, working_uid, working_gid)
                    shutil.move(file, target_path)
                    print("\Yay! sent: " + filename + "\nto: " + target_path)

                except:
                    print("Error moving file. Maybe it's already there?")

                os.chown(target_path, working_uid, working_gid)