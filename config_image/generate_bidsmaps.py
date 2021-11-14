#!/pythonlibs python3

'''
TODO: make files and directory structures if not exists

generate_bidsmaps.py

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
from collections import Counter
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

# Pass arguments as env vars from service launch script
project_id = os.environ['project_id']
# exam = str(os.environ['single_exam_no'])
# working_uid = int(os.environ['working_uid'])
# working_gid = int(os.environ['working_gid'])

project_path = '/Users/j/MRI_DATA/nyspi/' + project_id
bidsonly_path = '/bidsonly'
bids_config_path = '/bidsconfig'

token_path = '/tokens'
encrypted_file_path = token_path + '/xnat2bids_' + project_id + '_login.bin'

# Initialize variables
sequence_list = []
# Identifying keywords: add as needed
ignore = ['LOC','Localizer', '3Plane', 'EDT', 'ORIG', 'Screen_Save', 'CAL_ASSET', ':', 'Coronal', 'MRS']
accept = ['FUNC', 'DTI', 'STRUC']
t1s = ['t1','mprage', 'bravo', 'fspgr']
t2s = ['t2', 't2cube', 'cubet2']
fms = ['b0', 'fm_', 'topup', 'top-up']
strucs = t1s + t2s + ['struc']
funcs = ['func', 'fmri']
dtis = ['dti']
rs_names = ['rs', 'resting', 'restingstate']
not_rs = ['rsvp']

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

#............................................................
#         DECRYPT
#............................................................
with open(encrypted_file_path, "rb") as encrypted_file:
    # Where to find the private key  
    private_key_path = "/xnat/xnat2bids_private.pem"
    # Import and format the private key
    private_key = RSA.import_key(open(private_key_path).read())
    encrypted_session_key, nonce, tag, ciphertext = \
        [ encrypted_file.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]
    # Decrypt session key with private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(encrypted_session_key)
    # Decrypt the password with AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    username_password = cipher_aes.decrypt_and_verify(ciphertext, tag)
# Check if auth token was successfully decrypted and
# split username and password into separate variables
if len(username_password) > 0:
    # Remove this for production!
    username_password = str(username_password\
        .decode("utf-8"))\
            .strip()\
                .split()
    xnat_username = username_password[0].strip()
    xnat_password = username_password[1].strip()
else:
    print("Could not retrieve xnat login password. There was likely a problem retrieving or decrypting your login token.")
    
#............................................................
#   AUTHENTICATION: alias k:v tokens, then jsession token
#............................................................
# TODO: if login error, go back and run xnat-auth
xnat_url = 'https://xnat.nyspi.org'
alias_token_url_user = xnat_url + '/data/services/tokens/issue'
# alias_token_url_admin = alias_token_url_user + '/user/' + xnat_username

#.....................................................
#   1st session: request alias tokens (48hr life)
#.....................................................
session = requests.Session()    # Stores all the info we need for our session
session.auth = (xnat_username, xnat_password)
alias_response = session.get(alias_token_url_user)
alias_resp_text = alias_response.text
alias_resp_json = json.loads(alias_resp_text)
alias = alias_resp_json["alias"]
secret = alias_resp_json["secret"]
print("\nGenerated single-use alias.")
print("Generated single-use secret.")

# TODO: convert logic to use "with" to automatically close session

#.....................................................
#   2nd session: use the alias tokens to request JSESSION token
#.....................................................
jsession_url = xnat_url + '/data/JSESSION'
session = requests.Session()    # Stores all the info we need for our session
session.auth = (alias, secret)
jsession_id = session.post(jsession_url)

# Put JSESSION auth ID returned by XNAT rest api inside cookies header
# Now only the JSESSION ID is available to headers,
# Not even the temporary alias user and secret tokens are stored
session.text = {
    "cookies":
    {
        "JSESSIONID": jsession_id.text
    }
}

#password = getpass.getpass('Enter password: ')
# auth = {
#     'username': username,
#     'password': password,
#     'XNAT_CSRF': ''
# }

session_list_url = xnat_url + '/data/archive/projects/' + project_id + '/experiments?xsiType=xnat:mrSessionData&format=csv&columns=ID,label,xnat:subjectData/label'

# Todo: store password in .env variable

# Take input for project to scrape
# project_input = input("Enter project id to collect sequences for: ")
print('\n Awaiting response from server... This may take awhile depending on the size of the project. \n \n')
# Generate url to retrieve scans for a given project
session_url = 'https://xnat.nyspi.org/app/action/XDATActionRouter/xdataction/scanTypeCleanup/search_element/xnat%3AprojectData/search_field/xnat%3AprojectData.ID/search_value/' + project_id +'/popup/false'

# Import list of xnat projects
# Load (read) existing json JSON data to merge with new items
bidsmap_file = '/bidsconfig/bidsmap_' + project_id + '.json'
dcm2bids_file = '/bidsconfig/d2b-template_'+ project_id + '.json'

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

# Open XNAT session to access page with auth
try:
    with session.get(session_url) as res:
# try:
#     with requests.Session() as session:
#         session.auth = (xnat_username, xnat_password)
#         post = session.post(login_url, data=session.auth)
#         res = session.get(session_url)
        html = BeautifulSoup(res.content, 'html.parser')   # extract all html/xml from url and parse it

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

with open('/bidsconfig/logs/raw_list.txt', 'w') as tmp_file:
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

with open('/bidsconfig/logs/existing_bids.txt', 'w') as tmp_file:
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
with open('/bidsconfig/logs/sequence_list.txt', 'w') as tmp_file:
    tmp_file.write('\n'.join(map(str,sequence_list)))

# Filter out sequences that already exist in the map
not_in_map_bids = list(set(sequence_list).difference(existing_bids))
with open('/bidsconfig/logs/not_in_map_bids.txt', 'w') as tmp_file:
    tmp_file.write('\n'.join(map(str,not_in_map_bids)))

not_in_map_d2b = list(set(sequence_list).difference(existing_d2b))
with open('/bidsconfig/logs/not_in_map_d2b.txt', 'w') as tmp_file:
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
for i in not_in_map_bids:
    taskname = ''
    print(i)
    i_lower = i.lower()
    if any(x in i_lower for x in funcs) and not any(x in i_lower for x in fms):
        if re.match('func_mux.$', i_lower):
            taskname = 'untitled'
        elif i_lower.startswith('func_mux') or i_lower.startswith('func_epi'):
            # emperically, if the name starts with FUNC_MUX or FUNC_EPI then the task 
            # name is put in the 3rd column of _ separated list
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

#######################################################
#                          d2b
#######################################################
for i in not_in_map_d2b:
    print(i)
    taskname = ''
    run_number = ''
    i_lower = i.lower()
    if any(x in i_lower for x in funcs) and not any(x in i_lower for x in fms):
        if re.match('func_mux.$', i_lower):
            taskname = 'untitled'
        elif i_lower.startswith('func_mux') or i_lower.startswith('func_epi'):
            taskname = i_lower.split('_')[2]
        else:
            taskname = i_lower.split('_')[1]
        for element in i_lower.split('_'):
            if element.isdigit():
                if not element.isalpha():
                    run_number = element
        if any(y in taskname for y in rs_names) and not any(z in taskname for z in not_rs):
            taskname = 'rest'
        dataType = "func"
        modalityLabel = "bold"
        if len(run_number) > 0: 
            customLabels = 'task-' + taskname + '_run-0' + run_number
        else:
            customLabels = 'task-' + taskname

        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i}, "sidecarChanges": { "TaskName": taskname} }
        addSequence_d2b()

    # collect top-ups, discern between functional and dti top-up
    if any(x in i_lower for x in fms):
        taskname = i_lower.split('_')
        if len(taskname[1]) > 2:
            taskname = taskname[1]
        else:
            # skip empty string in index
            taskname = taskname[2]
        print("taskname for " + i_lower + ": " + taskname)
        if "rpe" in i_lower:
            if "topup" in taskname:
                customLabels = 'dir-rpe'
            else:
                customLabels = 'dir-' + taskname + 'rpe'
        elif "fpe" in i_lower:
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
        if any(x in i_lower for x in dtis):
            modalityLabel = "tensor"
        else:
            modalityLabel = "epi"
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i} }
        print("/n/n/n adding to d2b for " + i_lower)
        print(with_d2b)
        print()
        addSequence_d2b()
        continue

    # elif 'topup' in i_lower:
    #     taskname = i_lower.split('_')
    #     # some topups have a preceding "__" making the index choose an empty string
        
    #     if "rpe" in i_lower:
    #         customLabels = 'dir-' + taskname + 'rpe'
    #     elif "fpe" in i_lower:
    #         customLabels = 'dir-' + taskname + 'fpe'
    #     else:
    #         customLabels = 'dir-' + taskname + 'mv'
    #     dataType = "fmap"
    #     modalityLabel = "epi"
    #     with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i}}
    #     addSequence_d2b()

    elif 'asl' in i_lower:
        dataType = 'asl'
        modalityLabel = 'asl'
        with_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i}, "sidecarChanges": { "TaskName": taskname} }
        addSequence_d2b()
    # taskname=''

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

# Option to quit
# finish = input('\nSave file? (y/n): ')
# if finish == 'n':
#     print('\n Exiting \n')
#     sys.exit()

# Overwrite existing_json JSON file with old + new - duplicates
with open(bidsmap_file, 'w') as jsonFile:
    jsonFile.write(json.dumps(no_dupes, indent=4))
print('\nbidsmap file updated')

# Overwrite existing_json JSON file with old + new - duplicates
with open(dcm2bids_file, 'w') as jsonFile:
    jsonFile.write(json.dumps({"descriptions":updated_d2b}, indent=4))
print('\nd2b file updated. \n')
