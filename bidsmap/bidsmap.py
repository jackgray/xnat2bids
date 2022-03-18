#!/pythonlibs python3

'''
USAGE: generate_bidsmaps.py <project ID>

Generates two files, "bidsmap.json" and "d2b-map.json"

 Questions for Juan:
  1. What to do with B0 maps in d2b
  2. What to do with DTI and DTI topups in d2b
  Generally, get specific sequences to include and exclude from the maps
'''

# from lxml import html
import html5lib
from bs4 import BeautifulSoup
import requests
import re
import json
import time
import getpass
import sys
import os
import datetime
import os, stat
import errno
import requests
import datetime
import json
from shutil import rmtree
from subprocess import Popen



def bidsmap():
        
    # Initialize variables
    sequence_list = []
    # Identifying keywords: add as needed
    ignore = ['LOC','B0', 'Localizer', '3Plane', 'EDT', 'ORIG', 'Screen_Save', 'CAL_ASSET', ':', 'Coronal', 'MRS']
    accept = ['FUNC', 'DTI', 'STRUC']
    t1s = ['t1','mprage', 'bravo', 'fspgr']
    t2s = ['t2', 't2cube', 'cubet2']
    fmaps = ['fm_', 'topup', 'top-up']
    strucs = t1s + t2s + ['struc']
    funcs = ['func', 'fmri']
    dtis = ['dti']
    rs_names = ['rs', 'resting', 'restingstate']
    not_rs = ['rsvp', 'rsvpprf']

    existing_bids = []
    existing_d2b = []
    with_d2b={}
    generated_bids=[]
    generated_d2b=[]
    just_added_bids = []
    just_added_d2b=[]
    else_bids = []      # Place unfiltered sequences (else case) into array
    else_d2b = []
    to_skip = []

    # Import list of xnat projects
    # Load (read) existing json JSON data to merge with new items

    # Read what exists in bidsmap.json
    try:
        with open(bidsmap_file, mode='r') as jsonFile:
            existing_json_bids = json.load(jsonFile)
    except:
        existing_json_bids = []

    # Read what exists in d2b-map.json
    try:
        with open(dcm2bids_file, mode='r') as jsonFile:
            existing_json_d2b = json.load(jsonFile)
    except:
        existing_json_d2b = []

    # Add everything collected to a text file for reference
    raw_list = list(dict.fromkeys(raw_list))

    with open('/logs/raw_list.txt', 'w') as tmp_file:
        tmp_file.write('\n'.join(map(str,raw_list)))

    # Print sequences found on XNAT
    print(str(len(raw_list)) + ' unique sequences found: \n')
    for i in raw_list:
        print(i)
    print('----------------------------------------------------------')

    # Create a list of sequences already in the json file being read
    print('\nThe following sequences already exist in the bidsmap and will be skipped:\n')
   
    # Load bidsmap.json file
    for i in existing_json_bids:
        print(i['series_description'])
        existing_bids.append(i['series_description'])

    with open('/logs/existing_bids.txt', 'w') as tmp_file:
        tmp_file.write('\n'.join(map(str, existing_bids)))

    print('----------------------------------------------------------')

    print('\nThe following sequences already exist in the d2b file and will be skipped:\n')
    # Load d2b json file
    try:
        for i in existing_json_d2b['descriptions']:
            print(i['criteria']['SeriesDescription'])
            existing_d2b.append(i['criteria']['SeriesDescription'])
    except:
        print("empty list. no worries...")
    try:
        with open('logs/existing_d2b.txt', 'w') as tmp_file:
            tmp_file.write('\n'.join(map(str,existing_d2b)))
    except:
        print("Couldn't open logs/existing_d2b.txt. Does it exist?")
    print('----------------------------------------------------------')

    # Scan collected sequences for duplicates and remove them
    sequence_list = list(dict.fromkeys(sequence_list))
    with open('/logs/sequence_list.txt', 'w') as tmp_file:
        tmp_file.write('\n'.join(map(str,sequence_list)))

    # Filter out sequences that already exist in the map
    not_in_map_bids = list(set(sequence_list).difference(existing_bids))
    with open('/logs/not_in_map_bids.txt', 'w') as tmp_file:
        tmp_file.write('\n'.join(map(str,not_in_map_bids)))

    not_in_map_d2b = list(set(sequence_list).difference(existing_d2b))
    with open('/logs/not_in_map_d2b.txt', 'w') as tmp_file:
        tmp_file.write('\n'.join(map(str,not_in_map_d2b)))

    # Function to add generated scan info to a list
    def addSequence_bids():
        with_bids = {'series_description': i, 'bidsname': bidsname}
        generated_bids.append(with_bids)
        just_added_bids.append(i)
    def addSequence_d2b():
        generated_d2b.append(with_d2b)
        just_added_d2b.append(i)

    # Print sequences to be added to bidsmap
    print('\nAttempting to match the following ' + str(len(not_in_map_bids)) + ' sequences not yet in the bidsmap. \n')

    #######################################################
    #                          bidsmap
    #######################################################
    for add_series in not_in_map_bids:
        print("\nAdding ", add_series, " to bids map.")
        taskname = ''
        run_number = ''
        add_series = add_series.lower()
        if any(x in add_serie for x in funcs) and not any(x in add_series for x in fmaps):
            if re.match('func_mux.$', add_series):
                taskname = 'untitled'
            elif add_series.startswith('func_mux') or add_series.startswith('func_epi'):
                taskname = add_series.split('_')[2]
            else:
                taskname = add_series.split('_')[1]
            for element in add_series.split('_'):
                if element.isdigit():
                    if not element.isalpha():
                        run_number = element    # Discern if number in series name belongs to MUX factor or run number (or something else)
            
            if any(y in taskname for y in rs_names) and not any(z in taskname for z in not_rs):
                taskname = 'rest'

            if len(run_number) > 0: 
                taskname = taskname + '_run-0' + run_number
            # Uncomment below to have no-run-number names default to run-01
            # else:
            #     sidecar_name = sidecar_name + '_run-01'
            bidsname = 'task-' + taskname + '_bold'
            addSequence_bids()

        elif 'asl' in to_add:
            bidsname = 'asl'
            addSequence_bids()

        elif 'dti' in to_add:
            bidsname = 'dti'
            addSequence_bids()

        elif any(x in to_add for x in t1s) and not any(x in to_add for x in funcs):
            bidsname = 'T1w'
            addSequence_bids()

        # Find t2s but exclude funcs that have T2 in the name (ASSET2)
        elif any(x in to_add for x in t2s) and not any(x in to_add for x in funcs):
            bidsname = 'T2w'
            addSequence_bids()
        else:
            else_bids.append(add_series)
    print('----------------------------------------------------------')

    # Print sequences to be added to d2b
    print('\nAttempting to match the following ' + str(len(not_in_map_d2b)) + ' sequences not yet in the d2b-map. \n')

    #######################################################
    #                          d2b
    #######################################################
    for add_series in not_in_map_d2b:
        print(add_series)
        taskname = ''
        run_number = ''
        add_series = add_series.lower()
        if any(x in add_series for x in funcs) and not any(x in add_series for x in fmaps):
            if re.match('func_mux.$', add_series):
                taskname = 'untitled'
            elif add_series.startswith('func_mux') or add_series.startswith('func_epi'):
                taskname = add_series.split('_')[2]
            else:
                taskname = add_series.split('_')[1]
            for element in add_series.split('_'):
                if element.isdigit():
                    if not element.isalpha():
                        run_number = element
            if any(y in taskname for y in rs_names) and not any(z in taskname for z in not_rs):
                sidecar_name = taskname
                taskname = 'rest'
            dataType = "func"
            modalityLabel = "bold"
            if len(run_number) > 0: 
                customLabels = 'task-' + taskname + '_run-0' + run_number
            else:
                customLabels = 'task-' + taskname
            sidecar_name = taskname
            with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i}, "sidecarChanges": { "TaskName": sidecar_name} }
            addSequence_d2b()

        # collect top-ups, discern between functional and dti top-up
        if any(x in add_series for x in fmaps):
            taskname = add_series.split('_')
            if len(taskname[1]) > 2:
                taskname = taskname[1]
            else:
                # skip empty string in index
                taskname = taskname[2]
            print("taskname for " + add_series + ": " + taskname)
            if "rpe" in add_series:
                if "topup" in taskname:
                    customLabels = 'dir-rpe'
                else:
                    customLabels = 'dir-' + taskname + 'rpe'
            elif "fpe" in add_series:
                if "topup" in taskname:
                    customLabels = 'dir-fpe'
                else:
                    customLabels = 'dir-' + taskname + 'fpe'
            else:
                if "topup" in taskname:
                    customLabels = 'dir-mv'
                else:
                    customLabels = 'dir-' + taskname + 'mv'
            dataType = "fmap"
            if any(x in add_series for x in dtis):
                modalityLabel = "tensor"
            else:
                modalityLabel = "epi"
            with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i} }
            print("/n/n/n adding to d2b for " + add_series)
            print(with_d2b)
            print()
            addSequence_d2b()
            continue

        elif 'asl' in add_series:
            dataType = 'asl'
            modalityLabel = 'asl'
            with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i}, "sidecarChanges": { "TaskName": taskname} }
            addSequence_d2b()

        elif 'dti' in add_series:
            dataType = 'dti'
            modalityLabel = 'tensor'
            with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "criteria": { "SeriesDescription": i} }
            addSequence_d2b()

        elif any(x in add_series for x in t1s) and not any(x in add_series for x in funcs):
            dataType = "anat"
            modalityLabel = "T1w"
            with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "criteria": { "SeriesDescription": i} }
            addSequence_d2b()

        # Find t2s but exclude funcs that have T2 in the name (ASSET2)
        elif any(x in add_series for x in t2s) and not any(x in add_series for x in funcs):
            dataType = "anat"
            modalityLabel = "T2w"
            with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "criteria": { "SeriesDescription": i} }
            addSequence_d2b()
        else:
            else_d2b.append(i)
    print('----------------------------------------------------------')

    # Print what was just added
    if len(just_added_bids) > 0:
        print('\nGenerated bids maps for ' + str(len(just_added_bids)) + ' sequences: \n')
        for i in just_added_bids:
            print(i)
    else:
        print('\nNo new sequences were added to bidsmap file because they either do not fit matching criteria or already exist.\n')

    if len(just_added_d2b) > 0:
        print('\nGenerated d2b maps for ' + str(len(just_added_d2b)) + ' sequences: \n')
        for i in just_added_d2b:
            print(i)
    else:
        print('\nNo new sequences were added to d2b file because they either do not fit matching criteria or already exist.\n')

    # Keep track of sequences that didn't get added
    skipped_scans_bids = list(set(not_in_map_bids).difference(just_added_bids))
    skipped_scans_d2b = list(set(not_in_map_d2b).difference(just_added_d2b))
    # Sanity check: skipped_scans_bids/d2b should equal else_bids/d2b
    check_bids = list(set(else_bids).difference(skipped_scans_bids))
    check_d2b = list(set(else_d2b).difference(skipped_scans_d2b))

    if len(check_bids) > 0:
        print('\nSequences added to bids are not complimentary to sequences skipped. Check code.')
        for i in check_bids:
            print(i)
    if len(check_d2b) > 0:
        print('\nSequences added to bids are not complimentary to sequences skipped. Check code.')
        for i in check_d2b:
            print(i)

    if len(skipped_scans_bids) > 0:
        print('\n' + str(len(skipped_scans_bids)) + ' sequences were not added to bidsmap file because they either do not fit the bidsmap criteria or already exist. \n' )
        for i in skipped_scans_bids:
            print(i)

    if len(skipped_scans_d2b) > 0:
        print('\n' + str(len(skipped_scans_d2b)) + ' sequences were not added to d2b file because they either do not fit the d2b criteria or already exist. \n' )
        for i in skipped_scans_d2b:
            print(i)

    # Update existing_json JSON data with new elements
    updated_bids = generated_bids + existing_json_bids

    for i in updated_bids:
        print("updated_bids = ")
        print(i)
    for i in existing_json_bids:
        print("existing_json_bids = ")
        print(i)

    # Remove duplicates again
    no_dupes = { each['series_description'] : each for each in updated_bids}.values()
    no_dupes = list(no_dupes)

    # Update existing_json JSON data with new elements
    try:
        updated_d2b = generated_d2b + existing_json_d2b['descriptions']
    except:
        updated_d2b = generated_d2b

    # Write what this program added to the file in a separate file for debugging
    added = open('/bidsconfig/logs/add-history_bids.txt','a')
    added.write('\n\n\n' + str(datetime.datetime.now()) + '\n\n\n')
    added.write('\n\n'.join(map(str,generated_bids)))
    added.close()

    added = open('/bidsconfig/logs/add-history_d2b.txt','a')
    added.write('\n\n\n' + str(datetime.datetime.now()) + '\n\n\n')
    added.write('\n\n'.join(map(str,generated_d2b)))
    added.close()

    # Overwrite existing_json JSON file with old + new - duplicates
    with open(bidsmap_file, 'w') as jsonFile:
        jsonFile.write(json.dumps(no_dupes, indent=4))
    print('\nbidsmap file updated')

    # Overwrite existing_json JSON file with old + new - duplicates
    with open(dcm2bids_file, 'w') as jsonFile:
        jsonFile.write(json.dumps({"descriptions":updated_d2b}, indent=4))
    print('\nd2b file updated. \n')
