#!/usr/bin/env python3

# generate_bidsmaps.py

#  Generates two files, "bidsmap.json" and "d2b-map.json"

#  Questions for Juan:
#   1. What to do with B0 maps in d2b
#   2. What to do with DTI and DTI topups in d2b
#   Generally, get specific sequences to include and exclude from the maps

from lxml import html
from bs4 import BeautifulSoup
import requests
import re
import json
import time
import getpass
import sys
import os
import datetime

# Initialize variables
sequence_list = []

ignore = ['LOC','Localizer', '3Plane', 'EDT', 'ORIG', 'Screen_Save', 'CAL_ASSET', ':', 'Coronal', 'MRS']
accept = ['FUNC', 'DTI', 'STRUC']
t1s = ['t1','mprage', 'bravo', 'fspgr']
t2s = ['t2', 't2cube', 'cubet2']
fms = ['b0', 'fm_', 'topup', 'top-up']
strucs = t1s + t2s + ['struc']
funcs = ['func', 'fmri']
dtis = ['dti']

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

# Log in to XNAT
login_url = 'https://xnat.nyspi.org/login'

# Login credintials
username = input('Enter XNAT username: ')
password = getpass.getpass('Enter password: ')
auth = {
    'username': username,
    'password': password,
    'XNAT_CSRF': ''
}
# Todo: store password in .env variable

# Take input for project to scrape
project_input = input("Enter project id to collect sequences for: ")
print('\n Awaiting response from server... This may take awhile depending on the size of the project. \n \n')
# Generate url to retrieve scans for a given project
session_url = 'https://xnat.nyspi.org/app/action/XDATActionRouter/xdataction/scanTypeCleanup/search_element/xnat%3AprojectData/search_field/xnat%3AprojectData.ID/search_value/'+project_input+'/popup/false'

# Import list of xnat projects
# Load (read) existing json JSON data to merge with new items
bidsmap_file = 'json/bidsmap.json'
dcm2bids_config_filepath = 'json/dcm2bids_config.json'

# Read what exists in bidsmap.json
with open(bidsmap_file, mode='r') as jsonFile:
    existing_json_bids = json.load(jsonFile)

# Read what exists in d2b-map.json
with open(dcm2bids_config_filepath, mode='r') as jsonFile:
    existing_json_d2b = json.load(jsonFile)

# Open XNAT session to access page with auth
try:
    with requests.Session() as session:
        post = session.post(login_url, data=auth)
        res = session.get(session_url)
        html = BeautifulSoup(res.content, 'lxml')   # extract all html/xml from url and parse it

        # Sequence names are sorted in a column with a html <tr> tag
        trs = html.find_all('tr',{'valign':'top'}) # find all <tr> tags; narrow down index with formatting filters

        # Index each row of the 5th column (td[4]) by looking for the 5th occurrence of the td tag in each of the tr elements
        raw_list = []
        td = str
        for tr in trs:
            td = tr.find_all('input')[4]['value'].replace(' ', '_')
            raw_list.append(td)

            # Exclude sequences we don't care about
            if not any(x in td for x in ignore):
                sequence_list.append(td)
except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)

# Add everything collected to a text file for reference
raw_list = list(dict.fromkeys(raw_list))

with open('log/raw_list.txt', 'w') as tmp_file:
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
with open('log/existing_bids.txt', 'w') as tmp_file:
    tmp_file.write('\n'.join(map(str, existing_bids)))
print('----------------------------------------------------------')

print('\nThe following sequences already exist in the d2b file and will be skipped:\n')
# Load d2b json file
for i in existing_json_d2b['descriptions']:
    print(i['criteria']['SeriesDescription'])
    existing_d2b.append(i['criteria']['SeriesDescription'])
with open('log/existing_d2b.txt', 'w') as tmp_file:
    tmp_file.write('\n'.join(map(str,existing_d2b)))
print('----------------------------------------------------------')

# Scan collected sequences for duplicates and remove them
sequence_list = list(dict.fromkeys(sequence_list))
with open('log/sequence_list.txt', 'w') as tmp_file:
    tmp_file.write('\n'.join(map(str,sequence_list)))

# Filter out sequences that already exist in the map
not_in_map_bids = list(set(sequence_list).difference(existing_bids))
with open('log/not_in_map_bids.txt', 'w') as tmp_file:
    tmp_file.write('\n'.join(map(str,not_in_map_bids)))

not_in_map_d2b = list(set(sequence_list).difference(existing_d2b))
with open('log/not_in_map_d2b.txt', 'w') as tmp_file:
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

# Generate map for bidsmap file
for i in not_in_map_bids:
    print(i)
    i_lower = i.lower()
    if any(x in i_lower for x in funcs) and not any(x in i_lower for x in fms):
        if re.match('func_mux.$', i_lower):
            taskname = 'untitled'
        elif i_lower.startswith('func_mux') or i_lower.startswith('func_epi'):
            taskname = i_lower.split('_')[2]
        else:
            taskname = i_lower.split('_')[1]
        bidsname = 'task-' + taskname + '_bold'
        addSequence_bids()

    # elif any(x in i_lower for x in fms):
    #     else_bids.append(i)

    # elif 'topup' in i_lower:
    #     to_skip.append(i)

    elif 'asl' in i_lower:
        bidsname = 'asl'
        addSequence_bids()

    elif 'dti' in i_lower:
        bidsname = 'dti'
        addSequence_bids()

    elif any(x in i_lower for x in t1s) and not any(x in i_lower for x in funcs):
        bidsname = 'T1w'
        addSequence_bids()

    # Find t2s but exclude funcs that have T2 in the name (ASSET2)
    elif any(x in i_lower for x in t2s) and not any(x in i_lower for x in funcs):
        bidsname = 'T2w'
        addSequence_bids()
    else:
        else_bids.append(i)
print('----------------------------------------------------------')

# Print sequences to be added to d2b
print('\nAttempting to match the following ' + str(len(not_in_map_d2b)) + ' sequences not yet in the d2b-map. \n')

# Generate map for d2b file
for i in not_in_map_d2b:
    print(i)
    i_lower = i.lower()
    if any(x in i_lower for x in funcs) and not any(x in i_lower for x in fms):
        if re.match('func_mux.$', i_lower):
            taskname = 'untitled'
        elif i_lower.startswith('func_mux') or i_lower.startswith('func_epi'):
            taskname = i_lower.split('_')[2]
        else:
            taskname = i_lower.split('_')[1]
        dataType = "func"
        modalityLabel = "bold"
        customLabels = 'task-' + taskname
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i}, "sidecarChanges": { "TaskName": taskname} }
        addSequence_d2b()

    # collect top-ups, discern between functional and dti top-up
    elif any(x in i_lower for x in fms):
        taskname = i_lower.split('_')[1]
        if "rpe" in i_lower:
            customLabels = 'dir-' + taskname + '-rpe'
        elif "fpe" in i_lower:
            customLabels = 'dir-' + taskname + '-fpe'
        else:
            customLabels = 'dir-' + taskname + '-mv'
        dataType = "fmap"
        if any(x in i_lower for x in dtis):
            modalityLabel = "tensor"
        else:
            modalityLabel = "epi"
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i} }
        addSequence_d2b()

    # elif 'topup' in i_lower:
    #     taskname = i_lower.split('_')[1]
    #     if "rpe" in i_lower:
    #         customLabels = 'dir-' + taskname + '-rpe'
    #     elif "fpe" in i_lower:
    #         customLabels = 'dir-' + taskname + '-fpe'
    #     else:
    #         customLabels = 'dir-' + taskname + '-mv'
    #     dataType = "fmap"
    #     modalityLabel = "epi"
    #     with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i}}
    #     addSequence_d2b()

    elif 'asl' in i_lower:
        dataType = 'asl'
        modalityLabel = 'asl'
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i}, "sidecarChanges": { "TaskName": taskname} }
        addSequence_d2b()

    elif 'dti' in i_lower:
        dataType = 'dti'
        modalityLabel = 'tensor'
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "criteria": { "SeriesDescription": i} }
        addSequence_d2b()

    elif any(x in i_lower for x in t1s) and not any(x in i_lower for x in funcs):
        dataType = "anat"
        modalityLabel = "T1w"
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "criteria": { "SeriesDescription": i} }
        addSequence_d2b()

    # Find t2s but exclude funcs that have T2 in the name (ASSET2)
    elif any(x in i_lower for x in t2s) and not any(x in i_lower for x in funcs):
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

# Remove duplicates again
no_dupes = { each['series_description'] : each for each in updated_bids}.values()
no_dupes = list(no_dupes)

# Update existing_json JSON data with new elements
updated_d2b = generated_d2b + existing_json_d2b['descriptions']

# Write what this program added to the file in a separate file for debugging
added = open('log/add-history_bids.txt','a')
added.write('\n\n\n' + str(datetime.datetime.now()) + '\n\n\n')
added.write('\n\n'.join(map(str,generated_bids)))
added.close()

added = open('log/add-history_d2b.txt','a')
added.write('\n\n\n' + str(datetime.datetime.now()) + '\n\n\n')
added.write('\n\n'.join(map(str,generated_d2b)))
added.close()

# Option to quit
finish = input('\nSave file? (y/n): ')
if finish == 'n':
    print('\n Exiting \n')
    sys.exit()

# Overwrite existing_json JSON file with old + new - duplicates
with open(bidsmap_file, 'w') as jsonFile:
    jsonFile.write(json.dumps(no_dupes, indent=4))
print('\nbidsmap file updated')

# Overwrite existing_json JSON file with old + new - duplicates
with open(dcm2bids_config_filepath, 'w') as jsonFile:
    jsonFile.write(json.dumps({"descriptions":updated_d2b}, indent=4))
print('\nd2b file updated. \n')
