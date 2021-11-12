from lxml import html
from bs4 import BeautifulSoup
import requests
import re
#import pandas as pd
#import csv
import json
import time
import getpass
import sys
import os



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
#project_input = 'test'
project_input = input("Enter project id to collect sequences for: ")
print('\n Awaiting response from server... This may take awhile depending on the size of the project. \n \n')
# Generate url to retrieve scans for a given project
session_url = 'https://xnat.nyspi.org/app/action/XDATActionRouter/xdataction/scanTypeCleanup/search_element/xnat%3AprojectData/search_field/xnat%3AprojectData.ID/search_value/'+project_input+'/popup/false'

# Load (read) existing json JSON data to merge with new items
filename = 'bidsmap.json'
# Set full path if running in bundled app
if '_MEIPASS2' in os.environ:
    filename = os.path.join(os.environ['_MEIPASS2'], filename)
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
    ignore = ['LOC','ASL','TOP-UP', 'TOPUP', 'EDT', 'ORIG', 'Screen_Save', 'CAL_ASSET', 'RFE', 'B0', ':']
    accept = ['FUNC', 'DTI', 'STRUC']

    # Index each row of the 5th column (td[4]) by looking for the 5th occurrence of the td tag in each of the tr elements
    raw_list = []
    td = str
    for tr in trs:
        td = tr.find_all('input')[4]['value'].replace(' ', '_')
        raw_list.append(td)
    # Exclude sequences we don't care about
        if not any(x in td for x in ignore) and any(x in td for x in accept):
            sequence_list.append(td)

# Add everything collected to a text file for reference
raw_list = list(dict.fromkeys(raw_list))
print('Unfiltered sequences from project ' + project_input + ' saved to `unfiltered.txt`')
with open('unfiltered.txt', 'w') as tmp_file:
    tmp_file.write('\n'.join(map(str,raw_list)))

# Terminate if no sequences were found. Likely XNAT server timeout.
if td == False:
    print('Connection to XNAT failed. Try again.')
    sys.exit()

## Compare to existing bidsmap and remove sequences already mapped

existing = []
for scan in existing_json:
    existing.append(scan['series_description'])

print('\nCollected ' + str(len(sequence_list)) + ' total sequences from project `' + project_input + '`.')
time.sleep(3)

# Scan collected sequences for duplicates and remove them
print("\nStripping duplicates...")
time.sleep(3)

sequence_list = list(dict.fromkeys(sequence_list))
print('\n' + str(len(sequence_list)) + ' unique sequences that fit bids criteria: \n')
time.sleep(3)
print('\n'.join(map(str, sequence_list)))
collected_count = str(len(sequence_list))

# Filter out sequences that already exist in the map
not_in_map = list(set(sequence_list).difference(existing))
process_queue = not_in_map
# Put functional sequences in their own queue for progress tracking
func_queue = []
for i in process_queue:
    if 'FUNC' in i:
        func_queue.append(i)

### Generate bids map in JSON format

with_bids={}
generated_json=[]
just_added = []
t1s = ['T1', 'MPRAGE', 'BRAVO', 'FSPGR']
t2s = ['T2', 'T2CUBE', 'CUBET2']
funcs = ['FUNC', 'EPI']
not_funcs = ['STRUC', 'FSPGR', 'DTI']
dtis = ['DTI']

print('\nParsing FUNC scans... \n')

time.sleep(3)
if len(func_queue) > 0:
    print('\nTask names to be used in bids format name: \n')

# Most functional scans are either formated 'FUNC_MUX*_taskname_other-stuff'
# or 'FUNC_taskname_stuff_MUX*'
for i in process_queue:
    # Catch sequences that would cause index error
    if re.match('FUNC_MUX.$', i):
        taskname = 'untitled'
    elif i.startswith('FUNC_MUX') or i.startswith('FUNC_EPI'):
        taskname = i.lower().split('_')[2].rstrip('0123456789')
        print(taskname)
    elif 'FUNC' in i:
        taskname = i.lower().split('_')[1].rstrip('0123456789')
        print(taskname)
    else:
        continue
    bidsname = 'task-' + taskname +'_bold'
    with_bids = {'series_description': i, 'bidsname': bidsname}
    generated_json.append(with_bids)
    # Keep a list of sequences that were added by this script
    just_added.append(i)

# Remove just added sequences from queue
process_queue = list(set(process_queue).difference(just_added))

print('\nAdding new sequences to bids map... If sequence already exists in the map it will be skipped.\n')
if len(just_added) > 0:
    print('\n \n' + str(len(just_added)) + ' functional sequences automatically added. \n')
    for i in just_added:
        print(i)
time.sleep(3)

# Put functional sequences in their own queue for progress tracking
func_queue = []
for i in process_queue:
    if 'FUNC' in i:
        func_queue.append(i)

# Catch any functional sequences that did not get added
if len(func_queue) > 0:
    print('\n \nFunctional sequences that need a human: \n')
    for i in func_queue:
        print(i)
    # Scan through functional tasks to map bids name with user input
    taskname = ''
    while taskname != 'done':
        taskname = input("\n The sequences above did not find a match. To add them, enter the short name of any one of the functional tasks in the list above (new functional name must match at least some part of the original sequence). Type 'done' when finished.: ").lower()
        if taskname == 'done':
            break
        elif taskname == '':
            pass
        for i in process_queue:
            if re.findall(taskname, i, re.IGNORECASE):
                bidsname = 'task-'+ taskname + '_bold'
                # Pair bids format name with the original series name
                with_bids = {'series_description': i, 'bidsname': bidsname}
                # Add the pair to a list of other generated pairs
                generated_json.append(with_bids)
                just_added.append(i)
            # If a name is not provided, don't add it. (re-running script will only show what's left)
            else:
                continue

# Auto-generate bidsname for the remaining sequences that don't require help from the user
for i in process_queue:
    if 'ASL' in i:
        bidsname = 'asl'
    elif 'DTI' in i:
        bidsname = 'dti'
    elif any(x in i for x in t1s) and not any(x in i for x in funcs):
        bidsname = 'T1w'
    # Find t2s but exclude FUNCs that have T2 in the name (ASSET2)
    elif any(x in i for x in t2s) and not any(x in i for x in funcs):
        bidsname = 'T2w'
    else:
        continue
    with_bids = {'series_description': i, 'bidsname': bidsname}
    # Add sequence pair to the list of other generated pairs
    generated_json.append(with_bids)
    just_added.append(i)

if len(just_added) > 0:
    print('\n Other sequences added: \n' )
    for i in just_added:
        if 'FUNC' not in i:
            print(i)

# Update queue of sequences left to add
process_queue = list(set(process_queue).difference(just_added))

# Show user sequences that were just added
if len(str(generated_json)) > 0:
    print('\nGenerated JSON to be added to bids map: ')
    print('\n'.join(map(str, generated_json)))

## Todo: generate CSV file version of bidsmap.json
# # Create Pandas Dataframe and save sequence list to CSV
# df_bs = pd.DataFrame(no_dupes, columns=['series_description'])
# df_bs.to_csv('output.csv')

if len(just_added) > 0:
    print('\n \n' + str(len(just_added)) + ' sequences were added to the bids map. \n')
else:
    print('No new functional sequences matched. Sequences collected are likely already in the bids map.')

# MANUAL MODE: catch any sequences that were not automatically added
if len(process_queue) > 0:
    print('\nThe following ' + str(len(process_queue)) + ' sequences did not find a match and were not added. \n')

    for i in process_queue:
        if 'FUNC' in i:
            print(i)
    for i in process_queue:
        if 'FUNC' not in i:
            print(i)

    manual_mode = input('\nWould you like to individually assign a bids name to the remaining scans? (y/n): ')
    taskname = ''
    if manual_mode == 'y':
        for i in process_queue:
            taskname = input('Enter a bids name for ' + i + ' (press ENTER to skip or type `done`): ')
            if taskname == 'done':
                break
            elif taskname == '':
                continue
            if 'STRUC' in i:
                bidsname = taskname
            elif 'FUNC' in i:
                bidsname = 'task-'+ taskname + '_bold'
            else:
                continue
            # Pair bids format name with the original series name
            with_bids = {'series_description': i, 'bidsname': bidsname}
            # Add the pair to a list of other generated pairs
            generated_json.append(with_bids)
            print('added to bids map')
            # if taskname != 'done' or '':
            just_added.append(i)

# Keep track of sequences that didn't get added
skipped_scans = list(set(not_in_map).difference(just_added))

# Update existing_json JSON data with new elements
updated = generated_json + existing_json

# Remove duplicates again
no_dupes = { each['series_description'] : each for each in updated}.values()
no_dupes = list(no_dupes)

# Overwrite existing_json JSON file with old + new - duplicates
with open(jsonFilePath, 'w') as jsonFile:
    jsonFile.write(json.dumps(no_dupes, indent=4))

print('\n---------------------------------------------------------------------------- \n\nDone\n')
if len(just_added) > 0:
    print('\n' + str(len(just_added)) + ' sequences were added to the bids map.\n')
else:
    print('\nNo new sequences were added to bids map because they either could not be matched or already exist.\n')
#print('\n' + (len(
if len(skipped_scans) > 0:
    print('\n' + str(len(skipped_scans)) + ' sequences were not added because no bids names were given. Run this program again to add them. \n' )