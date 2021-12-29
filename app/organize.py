# move image paste here

from glob import glob
from os import path, walk, mkdir, remove, environ, chown, chmod
from shutil import move, rmtree

from setup import rawdata_path
from if_makedirs import if_makedirs
from fix_perms import fix_perms


def move2raw(exam_no, subject_id):
    
    print("\n\n************************** organize **********************\n")
    exam_path = '/bidsonly/' + exam_no
    unzipped_filepaths = glob(path.join(exam_path, "scans/*/*/*/*/*"))
    
    print("\nAttempting to organize these files in ", exam_path, ": ", unzipped_filepaths, "\n\n")
    subname = "sub-" + subject_id
    sesname = "ses-" + exam_no
    ses_path = path.join(rawdata_path, subname, sesname)
    anat_path = path.join(ses_path, 'anat')
    fmap_path = path.join(ses_path, 'fmap')
    func_path = path.join(ses_path, 'func')
     # Create directories for files to go to if they don't exist
    if_makedirs(anat_path)
    if_makedirs(func_path)
    if_makedirs(fmap_path)
    
    for scan_path in unzipped_filepaths:
        # Split up identifiers
        filename = scan_path.split('/')[-1]        
        # NIFTI 
        if filename.endswith('.nii.gz') or filename.endswith('.json'):
            print("\nDetected nifti or json file")
            # ses_path = path.join(rawdata_path, filename.split('_')[0], filename.split('_')[1])
            sequence_name = filename.split('_')[2]  # i.e. 'run-01'
            sequence_type = filename.split('_')[-1].split('.')[0]   # i.e. 'epi', 'T2w', 'T1w' (last element in filename by _ ([-1]), so we have to leave behind the extension ('.' ([0]))
        
            # Discern fmaps
            if 'dir-' in sequence_name: # 'dir' is unique to directional field-maps
                target_path = path.join(fmap_path, filename)
            # Discern anats
            elif 'w' in sequence_type: # w indicates T1w or T2w
                target_path = path.join(anat_path, filename)
            # Discern funcs
            elif 'bold' in sequence_type:
                target_path = path.join(func_path, filename)
                
        # DICOM -- for now we can assume that any dicom is a neuromelanin
        elif filename.endswith('.dcm'):
            print("\nDetected DICOM file. ")
            nm_path = path.join(ses_path, 'neuromelanin', )
            sequence_name = scan_path.split('/')[4]
            sequence_type = 'gre'
            target_path = path.join(nm_path, sequence_name, filename)
            # path.join(ses_path, scan_path.split('/')[-5])

        # Notify if files weren't sorted properly
        else:
            print("\n\n\nATTENTION!\n")
            print(filename)
            print("This file wasn't caught by my filter. I'm going to put it in this folder called 'sort', and you can decide what to do with it. If this is a re-ocurring issue, reach out to a member of the MRI computing department.")
            sort_path = ses_path + '/sort'
            target_path = path.join(sort_path, filename)
        
        if_makedirs(target_path)
        # Move the file 
        print("\nMoving: " + scan_path + "\nto: " + target_path)
        move(scan_path, target_path)
    
    fix_perms(path='/rawdata/' + subname)
    print('\n\nCleaning up /bidsonly directory...')
    # This folder should now be empty (sanity check)
    files_remaining = glob(exam_path + '/SCANS/*/*/*')
    if len(files_remaining) > 0:
        print("Uh oh! We have some stragglers. These files didn't get moved.")
        for i in files_remaining:
            print(i)
        print("\n Leaving original download as-is so you can decide what to do with these files. Remove the folder manually.")
    else:
        rmtree(exam_path)