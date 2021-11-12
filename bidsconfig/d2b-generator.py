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

# Log in to XNAT
login_url = 'https://xnat.nyspi.org/login'

# Login credintials
#username = input('Enter XNAT username: ')
username = 'grayjoh'
password = ''
#password = getpass.getpass('Enter password: ')
auth = {
    'username': username,
    'password': password,
    'XNAT_CSRF': ''
}
# Todo: store password in .env variable

# Take input for project to scrape
project_input = 'test'
#project_input = input("Enter project id to collect sequences for: ")
print('\n Awaiting response from server... This may take awhile depending on the size of the project. \n \n')
# Generate url to retrieve scans for a given project
session_url = 'https://xnat.nyspi.org/app/action/XDATActionRouter/xdataction/scanTypeCleanup/search_element/xnat%3AprojectData/search_field/xnat%3AprojectData.ID/search_value/'+project_input+'/popup/false'

# Import list of xnat projects
# Load (read) existing json JSON data to merge with new items
filename = 'dev_d2b-template.json'

jsonFilePath = filename
with open(jsonFilePath, mode='r') as jsonFile:
    existing_json = json.load(jsonFile)

# Open XNAT session to access page with auth
with requests.Session() as session:
    post = session.post(login_url, data=auth)
    res = session.get(session_url)
    html = BeautifulSoup(res.content, 'lxml')   # extract all html/xml from url and parse it

    # Sequence names are sorted in a column with a html <tr> tag
    trs = html.find_all('tr',{'valign':'top'}) # find all <tr> tags; narrow down index with formatting filters

    # Set parameters for scan types to collect and omit
    sequence_list = []
    ignore = ['LOC','Localizer', '3Plane', 'EDT', 'ORIG', 'Screen_Save', 'CAL_ASSET', ':', 'Coronal']
    accept = ['FUNC', 'DTI', 'STRUC']

    # Index each row of the 5th column (td[4]) by looking for the 5th occurrence of the td tag in each of the tr elements
    raw_list = []
    td = str
    for tr in trs:
        td = tr.find_all('input')[4]['value'].replace(' ', '_')
        raw_list.append(td)
    # Exclude sequences we don't care about
        if not any(x in td for x in ignore):
            sequence_list.append(td)

# Add everything collected to a text file for reference
raw_list = list(dict.fromkeys(raw_list))
with open('unfiltered.txt', 'w') as tmp_file:
    tmp_file.write('\n'.join(map(str,raw_list)))

print(str(len(raw_list)) + ' unique sequences found: \n')
for i in raw_list:
    print(i)

# Terminate if no sequences were found. Likely XNAT server timeout.
if td == False:
    print('Connection to XNAT failed. Try again.')
    sys.exit()

# Create a list of sequences already in the json file being read
existing = []
for i in existing_json['descriptions']:
    print(i['criteria']['SeriesDescription'])
    existing.append(i['criteria']['SeriesDescription'])
with open('existing.txt', 'w') as tmp_file:
    tmp_file.write('\n'.join(map(str,existing)))

# Scan collected sequences for duplicates and remove them
sequence_list = list(dict.fromkeys(sequence_list))
with open('sequence_list.txt', 'w') as tmp_file:
    tmp_file.write('\n'.join(map(str,sequence_list)))

# Filter out sequences that already exist in the map
not_in_map = list(set(sequence_list).difference(existing))
with open('not_in_map.txt', 'w') as tmp_file:
    tmp_file.write('\n'.join(map(str,not_in_map)))

# Print sequences to be added
print('\nFound ' + str(len(not_in_map)) + ' sequences that are not in the map. Parsing...\n')
# for i in not_in_map:
#     print(i)

# Function to add generated scan info to a list
def addSequence():
    generated_json.append(with_d2b)
    just_added.append(i)
#def toBids():


with_d2b={}
generated_json=[]
just_added = []
other = []

t1s = ['t1','mprage', 'bravo', 'fspgr']
t2s = ['t2', 't2cube', 'cubet2']
fms = ['b0', 'fm', 'topup', 'top-up']
strucs = t1s + t2s + ['struc']
funcs = ['func', 'fmri']
dtis = ['dti']

for i in not_in_map:
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
        addSequence()

    elif any(x in i_lower for x in fms):
        taskname = i_lower.split('_')[1]
        if "rpe" in i_lower:
            customLabels = 'dir-' + taskname + '-rpe'
        elif "fpe" in i_lower:
            customLabels = 'dir-' + taskname + '-fpe'
        else:
            customLabels = 'dir-' + taskname + '-mv'
        dataType = "fmap"
        modalityLabel = "epi"
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i} }
        addSequence()

    elif 'topup' in i_lower:
        taskname = i_lower.split('_')[1]
        if "rpe" in i_lower:
            customLabels = 'dir-' + taskname + '-rpe'
        elif "fpe" in i_lower:
            customLabels = 'dir-' + taskname + '-fpe'
        else:
            customLabels = 'dir-' + taskname + '-mv'
        dataType = "fmap"
        modalityLabel = "epi"
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i}}
        addSequence()

    elif 'asl' in i_lower:
        dataType = 'asl'
        modalityLabel = 'asl'
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i}, "sidecarChanges": { "TaskName": taskname} }
        addSequence()

    elif 'dti' in i_lower:
        dataType = 'dti'
        modalityLabel = 'tensor'
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "criteria": { "SeriesDescription": i} }
        addSequence()

    elif any(x in i_lower for x in t1s) and not any(x in i_lower for x in funcs):
        dataType = "anat"
        modalityLabel = "T1w"
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "criteria": { "SeriesDescription": i} }
        addSequence()

    # Find t2s but exclude funcs that have T2 in the name (ASSET2)
    elif any(x in i_lower for x in t2s) and not any(x in i_lower for x in funcs):
        dataType = "anat"
        modalityLabel = "T2w"
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "criteria": { "SeriesDescription": i} }
        addSequence()
    else:
        other.append(i)

# Print what was just added
if len(just_added) > 0:
    print('\nGenerated maps for ' + str(len(just_added)) + ' sequences: \n')
    for i in just_added:
        print(i)
else:
    print('\nNo new sequences were added to bids map because they either could not be parsed or already exist.\n')

# Print scans that were not added
#skipped_scans = list(set(not_in_map).difference(just_added))
if len(other) > 0:
    print('\n' + str(len(other)) + ' sequences could not be parsed and were not added to the map. \n' )
    for i in other:
        print(i)

# Update existing_json JSON data with new elements
updated = generated_json + existing_json['descriptions']

# Write what this program added to the file in a separate file for debugging
added = open('add-history.txt','a')
added.write('\n\n\n' + str(datetime.datetime.now()) + '\n')
added.write('\n\n'.join(map(str,generated_json)))
added.close()

# Option to quit
finish = input('\nSave file? (y/n): ')
if finish == 'n':
    print('\n Exiting \n')
    sys.exit()

# Overwrite existing_json JSON file with old + new - duplicates
with open(jsonFilePath, 'w') as jsonFile:
    jsonFile.write(json.dumps({"descriptions":updated}, indent=4))

print('\n File updated. \n')
