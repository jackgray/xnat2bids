from lxml import html
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import csv, json
import re

## This program will login to XNAT and retreive sequence names from any session url and generate a bidsmap json file from it. Navigate to a scan session and paste the url into the prompt. Then enter the short description for any functional tasks in the next prompt (e.g. "rest", or "sst")


# First login to XNAT
login_url = 'https://xnat.nyspi.org/login'

# login credintials
payload = {
    'username': 'grayjoh',
    'password': '',
    'XNAT_CSRF': ''
}
# todo: store password in .env variable

# take input for project to scrape
url_input = raw_input("enter url of sequence names to fetch: ")

# url_input = 'https://xnat.nyspi.org/app/action/DisplayItemAction/search_element/xnat:mrSessionData/search_field/xnat:mrSessionData.ID/search_value/XNATnyspi13_E00007/project/margtoxi'

# Load existing JSON data to merge with new items
jsonFilePath = 'bids.json'
with open(jsonFilePath, mode='r') as jsonFile:
    existing = json.load(jsonFile)

# Open XNAT session to access page with auth
with requests.Session() as session:
    post = session.post(login_url, data=payload)
    res = session.get(url_input)
    html = BeautifulSoup(res.content, 'lxml')   # extract all html/xml from url and parse it

    # Sequence names are sorted in a column with a html <tr> tag
    trs = html.find_all('tr',{'valign':'top'}) # find all <tr> tags; narrow down index with formatting filters

    # Index each row of the 4th column (td[3]) by looking for the 4th occurence of the td tag in each of the tr elements
    sequence_list = []
    ignore = ['LOC','ASL','TOP-UP', 'TOPUP', 'EDT', 'ORIG', 'Screen_Save', 'CAL_ASSET', 'RFE']
    accept = ['FUNC', 'DTI', 'STRUC']
    for tr in trs:
        td = tr.find_all('td')[3].get_text(strip=True).replace(' ', '_')
    # exclude sequences we don't care about
        if not any(x in td for x in ignore) and any(x in td for x in accept):
            sequence_list.append(td)
print ('\n    Collected ' + str(len(td)) + ' sequences from XNAT exam')
print('\n'.join(map(str, sequence_list)))
# scan collected sequences for duplicates and remove them

print "\n    Stripping duplicates... "
sequence_list = list(dict.fromkeys(sequence_list))
print('\n'.join(map(str, sequence_list)))

### Generate bids map in JSON format

with_bids={}
generated_json=[]
T1s = ['T1', 'MPRAGE', 'BRAVO']
# Determine if there are multiple types of functional tasks
more = 'y'
while more == 'y' or 'yes':
    taskname = raw_input("\n Enter the name of the func task : ").lower()
    for i in sequence_list:
        if re.findall(taskname, i, re.IGNORECASE):
            bidsname = 'task-'+ taskname + '_bold'
            with_bids = {'series_description': i, 'bidsname': bidsname}
            generated_json.append(with_bids)
    more = raw_input("Are there more functional tasks of a different name? yes=y / no=n) ")

# Generate bidsname
for i in sequence_list:
    if any(x in i for x in T1s):
        bidsname = 'T1w'
    elif 'T2' in i:
        bidsname = 'T2w'
    elif 'ASL' in i:
        bidsname = 'asl'
    elif 'DTI' in i:
        bidsname = 'dti'
    else:
        continue
    with_bids = {'series_description': i, 'bidsname': bidsname}
    # add sequence pair to root list
    generated_json.append(with_bids)

print '\n    Generated JSON to be added to bids map: '
print('\n'.join(map(str, generated_json)))

# # Create Pandas Dataframe and save sequence list to CSV
# df_bs = pd.DataFrame(no_dupes, columns=['series_description'])
# df_bs.to_csv('output.csv')

# update existing json data with new elements
updated = generated_json + existing
print '\n Updated bids map: '
print('\n'.join(map(str, updated)))

# remove duplicates again
no_dupes = { each['series_description'] : each for each in updated}.values()

with open(jsonFilePath, 'w') as jsonFile:
    jsonFile.write(json.dumps(no_dupes, indent=4))
