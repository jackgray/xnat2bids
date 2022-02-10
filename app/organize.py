# move image paste here

from glob import glob
import os
from shutil import move, rmtree

import constants
from if_makedirs import if_makedirs
from fix_perms import fix_perms


def move2raw(exam_no, subject_id):
    
    print("\n\n************************** organize **********************\n")
    exam_path = '/bidsonly/' + exam_no
    exam_folder_items = glob(exam_path + '/*')
    
    print("\nAttempting to organize files in ", exam_path, "\n\n")
    subname = "sub-" + subject_id
    sesname = "ses-" + exam_no
    
    if len(exam_folder_items) > 0:  # ensure list is not empty
        # FILTER NEUROMELANIN by presence of .zip files and gre in the name
        for exam_folder_item in exam_folder_items:
            # print("\nAnalyzing: ", exam_folder_item)
            if exam_folder_item.endswith('.zip') and '2dgre' in exam_folder_item:
                print("\nDetected Neuromelanin zip archives. ")
                sub_path = os.path.join(constants.neuromelanin_path, subname + "_" + exam_no)
                ses_path = os.path.join(sub_path, sesname)
                print("session path: ", ses_path)
                sequence_name = exam_folder_item.split('.')[0].split('/')[3]
                print("sequence name: ", sequence_name)
                sequence_type = 'gre'
                target_path = os.path.join(ses_path, 'NM', sequence_name) + '.zip'
                print("target path: ", target_path)

                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                print("\nMoving ", exam_folder_item, " to \n", target_path)
                move(exam_folder_item, target_path)
                fix_perms(path=sub_path)
            
            elif exam_folder_item.endswith('.zip') and '2gre' not in exam_folder_item:
                print("ERROR. Not sure what to do with this file: ")
                print(exam_folder_item)
                print("Putting it in /unsorted")
                target_path = '/bidsonly/unsorted/' + exam_no + '/' + os.path.basename(exam_folder_item)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                move(exam_folder_item, target_path)
                fix_perms(path='/bidsonly/unsorted')
            
            # Assume items that are directories are unarchived XNAT download that follows their REST directory schema (aka. 5-FUNC/resources/NIFTI/files/sub-....nii.gz)
            elif os.path.isdir(exam_folder_item):
                unzipped_filepaths = glob(os.path.join(exam_folder_item, '*/*/*/*/*'))
                                                            # ^ scans, ^5-FUNC/resources/NIFTI/files/sub-....nii.gz
                for scan_path in unzipped_filepaths:

                    filename = scan_path.split('/')[-1]        
                    # NIFTI 
                    if not filename.endswith('.dcm'):
                        # ses_path = path.join(rawdata_path, filename.split('_')[0], filename.split('_')[1])
                        sequence_name = filename.split('_')[2]  # i.e. 'run-01'
                        sequence_type = filename.split('_')[-1].split('.')[0]   # i.e. 'epi', 'T2w', 'T1w' (last element in filename by _ ([-1]), so we have to leave behind the extension ('.' ([0]))
                        sub_path = os.path.join(constants.rawdata_path, subname)
                        ses_path = os.path.join(sub_path, sesname)
                        # Create directories for files to go to if they don't exist
                        anat_path = os.path.join(ses_path, 'anat')
                        fmap_path = os.path.join(ses_path, 'fmap')
                        func_path = os.path.join(ses_path, 'func')
                        dti_path = os.path.join(ses_path, 'dti')
                        # if_makedirs(anat_path)
                        # if_makedirs(func_path)
                        # if_makedirs(fmap_path)
                        # Discern fmaps
                        # if 'dir-' in sequence_name:
                        fmaps = ['dir','topup','top-up', 'mv', 'fpe', 'rpe']
                        notfmaps = ['dwi','dti', 'acq']
                        anats = ['T1', '2w', '1w', 'T2', 'struc']
                        notanats = [ 'dwi', 'dti', 'topup', 'fm', 'mv']
                        diffusion = ['acq','dir','dti','dwi']
                        notdti= ['topup','fmap','fm','top-up', 'mv']
                        funcs = ['task', 'bold', 'run']
                        notfuncs=['mv','topup']
                        # Catch fmaps
                        if any(item in scan_path for item in fmaps) and not any(item in scan_path for item in notfmaps): # 'dir' is unique to directional field-maps
                            target_path = os.path.join(fmap_path, filename)
                        # Catch anats
                        elif any(item in scan_path for item in anats) and not any(item in scan_path for item in notanats):
                            target_path = os.path.join(anat_path, filename)
                        # Catch funcs
                        elif any(item in scan_path for item in funcs) and not any(item in scan_path for item in notfuncs):
                            target_path = os.path.join(func_path, filename)
                        # Catch diffusion
                        elif any(item in scan_path for item in diffusion) and not any(item in scan_path for item in notdti):
                            target_path = os.path.join(dti_path, filename)
                            
                    # DICOM -- for now we can assume that any dicom is neuromelanin
                    elif filename.endswith('.dcm'):
                        print("\nDetected Neuromelanin DICOMS. ")
                        sub_path = os.path.join(constants.neuromelanin_path, subname)
                        ses_path = os.path.join(sub_path, sesname)
                        nm_path = os.path.join(ses_path, 'NM')  # Other datatypes may exist in /neuromelanin
                        sequence_name = scan_path.split('/')[4]
                        sequence_type = 'gre'
                        target_path = os.path.join(nm_path, sequence_name, filename)
                        # path.join(ses_path, scan_path.split('/')[-5])

                    # Notify if files weren't sorted properly
                    else:
                        print("\n\n\nATTENTION!\n")
                        print(filename)
                        print("This file wasn't caught by my filter. I'm going to put it in this folder called 'unsorted', and you can decide what to do with it. If this is a re-ocurring issue, reach out to a member of the MRI computing department.")
                        sort_path = '/bidsonly/unsorted'
                        target_path = os.path.join(sort_path, filename)
                    
                    # Move the file 
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    print("\nMoving: " + scan_path + "\nto: " + target_path)
                    try:
                        move(scan_path, target_path)
                    except:
                        print("Could not move scans because data already exists")
                    # print("Removing ", os.path.dirname(scan_path))
                    # rmtree(path.dirname(scan_path))
                    fix_perms(path=sub_path)  # set dir to subject path so parent directory isn't affected
            else:
                print("\nEncountered unknown filetype, ", os.path.basename(exam_folder_item), ".\nPlacing it in /unsorted")
                # UNCATEGORIZED FILES
                # put in folder with user input keyword describing data
                # or not if no keyword input was given
                if len(constants.keywords > 0):
                    target_path = '/bidsonly/unsorted/' + exam_no + '/' + constants.keywords[0] + '/' + os.path.basename(exam_folder_item)
                else:
                    target_path = '/bidsonly/unsorted/' + exam_no + '/' + os.path.basename(exam_folder_item)

                makedirs(target_path)
                move(exam_folder_item, target_path)
                fix_perms(path=target_path)

    else:
        print("\nCouldn't find any files to sort.")        
           
    # fix_perms(path='/rawdata/' + subname)
    print('\n\nCleaning up /bidsonly directory...')

    # This folder should now be empty (sanity check)
    files_remaining = glob(exam_path + '/SCANS/*/*/*')
    if len(files_remaining) > 0:
        print("Uh oh! We have some stragglers. These files didn't get moved.")
        for i in files_remaining:
            print(i)
        print("\n Leaving original download as-is with remaining files so you can decide what to do with these files. Remove the folder manually.")
    else:
        rmtree(exam_path)
        print("Removed directory ", exam_path)