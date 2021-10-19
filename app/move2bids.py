#!/pythonlibs python3

'''
usage: python3 nifti2bids.py <project ID>

This program is designed to take the project_id as single argument
which points to the working.lst for that project.

It can also be called from xnat2bids.py to run immediately after dn_nifti.py
'''


# bids src: /MRI_DATA/nyspi/<project_id>/derivativs/bidsonly/<exam_no>/scans/<series_no>/<BIDS>|<NIFTI>/<file>.json|.nii 
# bids dst: /MRI_DATA/nyspi/<project_id>/rawdata/sub-*/ses-*/anat|fmap|func/*.json|*.nii.gz

## TODO: what to do with scans.tsv & dataset_description.json

if not 'project_id' in locals():
    print('Project ID was not passed into this function from index.py. \n\
Searching for runtime arguments.')
    
    # import argparse
    from os import environ as env

    # parser = argparse.ArgumentParser(description='Download output of dcm2bids from XNAT.')
    # parser.add_argument("project_id")
    # args = parser.parse_args()

    # project_id = args.project_id
    # print("Set project ID as " + project_id)

    project_id = env['project_id']


# Make entire process a function so it can run under xnat2bids.py
# or on its own.
def move2bids(exam_no, subj_id):

    import argparse
    import os
    import shutil
    import glob
    # import unzip

    project_id = os.environ['project_id']
    project_path = '/MRI_DATA/nyspi/' + project_id

    
    # # working.lst format: <subj_id> ' ' <project_id> ' ' <exam_no> ' ' XNATnyspi20_E00253
    # exam_no = args[2]
    # project_id = args[1]
    # subj_id = args[0] 

    # Define paths
    # dn_nifti --> /derivatives/bidsonly
    bidsfiles_src = '/derivatives/bidsonly/' + exam_no + '/'
    
    # Use glob to pull paths to every file
    file_dirs = glob.glob(bidsfiles_src + 'SCANS/*/*/*')
    rawdata_path = '/rawdata/'
    
    # print("\nThis script will attempt to organize the following files: \n")
    # for file_dir in file_dirs:
    #     print(file_dir)

    for file in file_dirs:
        
        filename = file.split('/')[-1]
        print('FILENAME= ' + filename)

    # Create destination folders

        # Subject dir
        subname = filename.split('_')[0]
        sub_path = rawdata_path + subname
        if not os.path.isdir(sub_path):
            print('Creating directory ' + sub_path)
            os.mkdir('/rawdata')
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


if __name__ == '__main__':
    move2bids(exam_no, subj_id)
