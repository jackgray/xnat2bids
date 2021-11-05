#!/pythonlibs python3

'''
usage: python3 dn_nifti.py <project ID>

This program no longer takes arguments in the traditional way. Instead,
they are passed as environment variables in the docker image and defined
using python's environ library.

To run this script locally, your full project path must be added to path variables

TODO: 
4. remove trailing whitespace from working.lst file reads
or replace working.lst with exam_no only list file or detect single
exam no as string
5. refactor this shit
6. implement logging
'''

import os
import errno
import requests
import datetime
import json
from shutil import rmtree
from zipfile import ZipFile
from subprocess import Popen
from collections import Counter
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

# Pass arguments as env vars from service launch script
project_id = os.environ['project_id']
single_exam_no = os.environ['single_exam_no']
working_uid = int(os.environ['working_uid'])
working_gid = int(os.environ['working_gid'])
run_one_shot = False
if single_exam_no != 'undefined':
    run_one_shot = True

project_path = '/MRI_DATA/nyspi/' + project_id
bidsonly_path = '/bidsonly'
working_list_file = project_id + '_working.lst'
working_list_path = '/scripts/' + working_list_file
token_path = '/tokens'
encrypted_file_path = token_path + '/xnat2bids_' + project_id + '_login.bin'

#............................................................
#         DECRYPT
#............................................................
with open(encrypted_file_path, "rb") as encrypted_file:
        
    private_key_path = "/xnat/xnat2bids_private.pem"
    
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
#   working.lst ARGUMENT PARSER
#............................................................

if run_one_shot:
    download_queue = single_exam_no
    print("Detected single exam mode. Downloading " + download_queue + " only.")
    jobs = [single_exam_no]
    for job in jobs:
        arglist = job
    
        exam_no = job
    download_queue = set()
    active_job_no = 0
    total_jobs=len(jobs)
    print("\n" + str(total_jobs) + " jobs found in working list:\n")
    print("(Grabbing " + exam_no + " as exam number)\n")
    download_queue.add(exam_no)

else:
    print("\n\nTrying to read from working list path: ' + working_list_path")
    print('Time to access file could depend on /MRI_DATA i/o load...')

    # Pull just exam numbers from working list. It's all we need.   
    # working.lst format: <subj_id> '\t' <project_id> '\t' <exam_no> '\t' XNATnyspi20_E00253
    with open(working_list_path) as f:
        jobs = [f.readlines()]

    for job in jobs:
        arglist = job.split()
        for arg in arglist:
            print("arglist: " + arg)

        if len(arglist) == 1:
            exam_no = job.strip()
        elif len(arglist) > 1:
            exam_no = job.split()[2].strip()
        else:
            print("length of arglist is: " + len(arglist))
        download_queue = set()
        active_job_no = 0
        total_jobs=len(jobs)
        print("\n" + str(total_jobs) + " jobs found in working list:\n")
        print("(Grabbing " + exam_no + " as exam number)\n")
        download_queue.add(exam_no)
    
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
resources = 'BIDS,NIFTI'
session_list_url = xnat_url + '/data/archive/projects/' + project_id + '/experiments?xsiType=xnat:mrSessionData&format=csv&columns=ID,label,xnat:subjectData/label'

#................................................
#.......... GET SESSION LIST FROM XNAT ..........
#................................................
dt = datetime.datetime.now()
year_month_day = str(dt.year) + str(dt.month) + str(dt.day)
session_list_csv = bidsonly_path + '/XNAT_metadata/mrsessions_' + year_month_day + '.csv'
print("\nChecking for mrsessions.csv file (should be in " + bidsonly_path + ')...')
print('If it doesn\'t exist, we will attempt to download it.')

# Create directory for session list csv file
if not os.path.exists(os.path.dirname(session_list_csv)):
    try:
        print("Creating directory structure for " + session_list_csv.split('/')[-1])
        os.makedirs(os.path.dirname(session_list_csv))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

with open(session_list_csv, 'wb') as f:
    print("Opening csv file to write exams list to...")
    with session.get(session_list_url, stream=True) as r:
        print("Checking status...")
        if not r.raise_for_status():
            print("no status returned")
        print("Writing file (this could take some time depending on doctor i/o load)...")
        # download in chunks to save buffer memory on doctor
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)

#................................................
#...........DOWNLOAD SCANS FROM XNAT.............
#................................................
# Read mrsession csv and extract labels
# Scans will ultimately be downloaded by their session label
with open (session_list_csv, 'r') as f:
    print("Reading and parsing session csv file...")
    lines = f.readlines()
lines.pop(0)    # Remove 1st line of column labels as they are not exams
labels = []
print("\nPulled info on " + str(len(lines)) + " sessions.")
mrsession_ids = []

print("\n\n\nDOWNLOAD QUEUE")
print(download_queue)
print("\n\n\n")
# label: what the xnat csv calls an exam number -- label=exam_no
for line in lines:
    # args = job.split()
    arg_no = 0
    label = line.split(',')[-2]
    # 

    # Pull accession_no from list of project sessions if exam number
    # matches input args and only download those exams
    # print('Scanning list for requested exams...')
    if label in download_queue:

        active_job_no += 1
        print("\nJob " + str(active_job_no) + ' of ' + str(total_jobs) + ": " )
        print('\nFound accession no. for exam ' + str(label) + " on XNAT. Checking that the data doesn't already exist. If not, we'll try to download it using these input arguments...\n")
        # print(*args)
        print("\n")

        bidsonly_exam_path = bidsonly_path + '/' + label
    
        mrsession_id = line.split(',')[0]
        print("Adding " + mrsession_id + " to download queue.")
        mrsession_ids.append(mrsession_id)
        
        scan_download_url = str(xnat_url + '/data/experiments/' + mrsession_id + '/scans/ALL/resources/' + resources + '/files?format=zip&structure=legacy')
        unzipped_path = bidsonly_path + '/' + label
        zipfile = label + '.zip'
        zipfile_path = bidsonly_path + '/' + zipfile

        print('Entering scan download stage...')
        # IF UNZIPPED EXAM FOLDER EXISTS DO NOT WRITE
        # TODO: Implement checksums to patch missing data seamlessly
        if not os.path.exists(unzipped_path):
            try:
                print("Creating directory structure for " + zipfile)
                os.makedirs(os.path.dirname(zipfile_path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
                print("Error occured creating path for " + zipfile_path)
        else:
            print(unzipped_path + "\n\nDirectory exists for " + exam_no + ". \nAttempting to organize files into /rawdata per bids guidance.")
        # WRITE ZIPFILE 
        with open(zipfile_path, 'wb') as f:
            print("Opening file to write response contents to...")
            with session.get(scan_download_url, stream=True) as r:

                print("Checking status...")
                if not r.raise_for_status():
                    print("no status raised (good)")
                # TODO: good chunk size??
                chunk_size = 8192   # 256mb 
                try:
                    print("Writing zip file for exam " + exam_no + " in " + str(chunk_size) + "kb chunks...")                                                                                                                                                                                                                                                                                                                                                                                                                                              
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                    print("Download complete. Fixing permissions on zipfile: " + zipfile_path)
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
                    print("Error occured writing zip file.")
        os.chown(zipfile_path, working_uid, working_gid)

        continue




        # Session closes automatically after "with" statement
                
                # Alternatively, we can use subprocess.popen() to call
                # a shell command, like rsync
                # p = Popen(["nohup", "rsync", "-bwlimit=10000", "" scan_download_url])
        
        # # Unzip
        # try:
        #     with ZipFile(zipfile_path, 'r') as zipObj:
        #         print("Attempting to unzip...")
        #         zipObj.extractall(bidsonly_path)
        #     print("Extraction complete. Fixing permissions for zipfile...")
        #     os.chown(zipfile_path, working_uid, working_gid) 
        # except: 
        #     print("Encountered a problem while unzipping.")

                                            
        # # Delete zip file only if download completed successfully
        # if os.path.isdir(bidsonly_path + '/' + exam_no):
        #     print("File unzipped. Check " + bidsonly_path)
        #     print("Attempting to remove zip")
        #     host_zip_path = project_path + zipfile_path
        #     try:
        #         print("Fixing permissions for zipfile on host.")
        #         os.chown(host_zip_path, working_uid, working_gid)
        #     except:
        #         print("Error occurred while changing permissions on the host zipfile.")
        #     try:
        #         rmtree(host_zip_path)
        #     except OSError as exc:
        #         if exc.errno != errno.EEXIST:
        #             raise
        #         print("Could not remove host zip path.")
        # else:
        #     print("There was a problem and we were unable to extract the downloaded files. Check if the download completed successfully.")            
        
        # # Check if zip is still there for some reason (remove later)
        # if os.path.exists(zipfile_path):
        #     print("There was a problem deleting the zip file " + zipfile_path + ". This is a permissions issue we are working on. Bear with us!")


print("\n\n\nFIN!\n\n\n")