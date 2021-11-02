

import os
import shutil
from glob import glob
from os import environ as env
from zipfile import ZipFile

prepath = '/Users/j/MRI_DATA/nyspi/patensasc'
# Get list of data inside /bidsonly
bidsonly_path = prepath+'/derivatives/bidsonly'
bidsonly_items = glob(bidsonly_path + '/*')
# Get list of subjects inside /rawdata 
rawdata_path = prepath+'/rawdata'
rawdata_items = glob(rawdata_path + '/*')
print('subraw:')
print(rawdata_items)
# Fix permissions in /bidsonly
for item in rawdata_items:
    print("/rawdata: Fixing permissions on folder " + item)
    os.chown(item, working_uid, working_gid)

# Filter items in /bidsonly and ex
zips = []
not_exams = []
# Create a dict for exams and their files to move
move_queue = {}
if len(bidsonly_items) > 0:
    
    # Only run this program if /bidsonly is not empty
    print("Detected exam folder(s): ")
    for exam in bidsonly_items: 
        print(exam)

        if '.zip' in exam:
            zips.append(exam.split('.')[0])
        elif exam.isalpha():
            print(exam + " doesn't seem to be an exam. Skipping.")   
            not_exams.append(exam)
        elif '.' in exam:
            print(exam + " doesn't seem to be an exam. Skipping.")

        files2move = glob(exam + '/SCANS/*/*/*')
        move_queue.update({exam:[]})
        print(files2move)
        for file in files2move:
            print("file to move: " + file)
            if not isinstance(move_queue[exam], list):
                move_queue[exam] = [move_queue[exam]]
            move_queue[exam].append(file)
        
    # Compare zipfile names to folder names and extract appropriate zipfiles
    # for i in zips.intersection(files2move):
    #     print(i + 'already unzipped. Removing zip file ' + i + ' .zip')
    #     zips.pop(i)
    # for zip in zips:
    #     zipfile = zip + '.zip'
    #     print("Extracting " + zipfile + ' ...')
    #     with ZipFile(zipfile, 'r') as zip:
    #         zip.printdir()
    #         zip.extractall()
    #         print("Done.")
    
    # print("\nThis script will attempt to organize the following files: \n")
    # for file_dir in file_dirs:
    #     print(file_dir)
    
    for i in move_queue.keys():
        path = i.split('/')
        for filename in path:
            print('Moving file: ' + filename)
        # Create destination folders
            # Subject dir
            subname = filename.split('_')[0]
            sub_path = rawdata_path + '/' + subname
            if not os.path.isdir(sub_path):
                print('Creating directory ' + sub_path)
                # os.mkdir(sub_path)
            
        
