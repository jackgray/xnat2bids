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
# Fix permissions in /rawdata
for item in bidsonly_items:
    print("/rawdata: Fixing permissions on folder " + item)
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

# Filter items in /bidsonly and ex
zips = []
not_exams = []
# Create a dict for exams and their files to move
move_queue = {}
def poll(bidsonly_items):
    # Collect queues: files to unzip, unzipped folders to move
    for exam in bidsonly_items: 
        print(exam)

        # Create queue by exam number for zipfiles (remove .zip extension)
        if '.zip' in exam:
            zips.append(exam.split('.')[0])
        # If there are letters then this is not an exam folder
        elif exam.isalpha():
            print(exam + " doesn't seem to be an exam. Skipping.")   
            not_exams.append(exam)
        # If there are only numbers this is probably an exam folder
        elif exam.isnumeric and 'zip' not in exam:
            print(exam + " looks like data that needs sorting")

            files2move = glob(exam + '/SCANS/*/*/*')
            if len(files2move) > 0:
                examno = exam.split('/')[-1]

                move_queue.update({examno:[]})
            else:
                print("Exam folder '" + exam + "' is empty. Files have probably already been sorted.")
            print("files2move glob ")
            print(files2move)
            for file in files2move:
                print("file to move: " + str(file))
                if not isinstance(move_queue[examno], list):
                    print('move queue dict: ')
                    print(move_queue)

                    move_queue[examno] = [move_queue[examno]]
                move_queue[examno].append(file)
                print('movequeue[examno] : ')
                print(move_queue[examno])

def unzip(zips):
    if len(zips) > 0:
        for zip in zips:
            zipfile = zip + '.zip'
            print("Extracting " + zipfile + ' ...')
            with ZipFile(zipfile, 'r') as zip:
                zip.printdir()
                try:
                    zip.extractall(path='/bidsonly')
                    print("Done.")
                    try:
                        os.rmdir(zipfile)
                    except:
                        print("unable to remove directory")
                except:
                    print("could not unzip. disk quota error")
           
        

if len(bidsonly_items) > 0:
    
    # Only run this program if /bidsonly is not empty
    print("Detected exam folder(s): ")

    poll(bidsonly_items)
    unzip(zips)
    bidsonly_items = glob(bidsonly_path + '/*')
    poll(bidsonly_items)
    for k, v in move_queue.items():
        print(k,v)
        
    # Compare zipfile names to folder names and extract appropriate zipfiles
    # for i in zips.intersection(files2move):
    #     print(i + 'already unzipped. Removing zip file ' + i + ' .zip')
    #     zips.pop(i)
    
    # print("\nThis script will attempt to organize the following files: \n")
    # for file_dir in file_dirs:
    #     print(file_dir)

    
    for examno in move_queue.keys():
        print('i, move queue ')
        print(examno)
        exam_files = glob('/bidsonly/' + examno + '/SCANS/*/*/*')
        print('exam_files glob: ' + exam_files)
        for path in exam_files:
            file = path.split('/')[-1]
            print('file: ' + str(file))
        
        # Create destination folders
            # Subject dir
            subname = file.split('_')[0]
            print("subname: " + str(subname))
            sub_path = rawdata_path + '/' + subname
            if not os.path.isdir(sub_path):
                print('Creating directory ' + str(sub_path))
                # os.mkdir(sub_path)
            
        
    #     # Session dir
    #     sesname = filename.split('_')[1]
    #     ses_path = sub_path + '/' + sesname 
    #     if not os.path.isdir(ses_path):
    #         print('Creating directory ' + ses_path)
    #         os.mkdir(ses_path)
        
    # # Sort sequence type into /anat, /func, /fmap
    #     # make folders if they don't exist
    #     anat_path = ses_path + '/anat'
    #     if not os.path.isdir(anat_path):
    #         print('Creating directory ' + anat_path)
    #         os.mkdir(anat_path)

    #     fmap_path = ses_path + '/fmap'
    #     if not os.path.isdir(fmap_path):
    #         print('Creating directory ' + fmap_path)
    #         os.mkdir(fmap_path)
        
    #     func_path = ses_path + '/func'
    #     if not os.path.isdir(func_path):
    #         print('Creating directory ' + func_path)
    #         os.mkdir(func_path)
        
    #     sequence_name = filename.split('_')[2]  # i.e. 'run-01'
    #     print("sequence name: " + sequence_name)
    #     sequence_type = filename.split('.')[0].split('_')[-1]   # i.e. 'epi', 'T2w', 'T1w'
    #     print("sequence_type: " + sequence_type)

    #     # Move fmaps
    #     if 'dir-' in sequence_name:
    #         target_path = fmap_path
        
    #     # Move anats
    #     elif 'w' in sequence_type:
    #         target_path = anat_path
        
    #     # Move funcs
    #     elif 'bold' in sequence_type:
    #         target_path = func_path
        
    #     # Notify if files weren't sorted properly
    #     else:
    #         print("\n\n\n                             ATTENTION!!!!! \n\n\nthe following files will be moved to a directory called \'sort\' because they were not caught by this program's matching criteria.")
    #         print(filename)
    #         sort_path = ses_path + '/sort'
    #         if not os.path.isdir(sort_path):
    #             print('Creating directory ' + sort_path + ' to catch else cases.')
    #             os.mkdir(sort_path)
    #             shutil.move(file, sort_path)
        
    #     print("\nSending: " + filename + "\nto: " + target_path)
    #     shutil.move(file, target_path)

    #     os.chown(target_path, 2019, 2029)
else:
    print("/bidsonly folder seems to be empty. Nothing to move. Exiting.")