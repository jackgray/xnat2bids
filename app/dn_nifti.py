#!/usr/bin/python3

# NOTE: xnat_rsa passphrase = d#n*nifti$nyspi@doctor
# psych--no passphrase for now

'''
usage: python3 dn_nifti.py <project ID>

This program is designed to take the project_id as single argument
which points to the working.lst for that project.

It can also be called from index.py to run immediately after dn_nifti.py

TODO: best auth security without manual login
3. remove trailing whitespace from working.lst file reads
4. refactor this shit
'''

# First check if this script is being run from xnat2bids.py
# in which case the project_id variable will already be defined
if not 'project_id' in locals():
    print('Project ID was not passed into this function from index.py. \n\
        searching for runtime arguments.')
    import argparse

    parser = argparse.ArgumentParser(description='Download output of dcm2bids from XNAT.')
    parser.add_argument("project_id")
    args = parser.parse_args()

    project_id = args.project_id
    print("Found project id " + project_id + "as arg")

def download_niftis(project_id):

    print('Project ID: ' + project_id)

    import os
    import errno
    import requests
    import datetime
    import json
    import getpass
    from zipfile import ZipFile
    from subprocess import Popen
    import decrypt
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import AES, PKCS1_OAEP

    project_path = '/Users/j/MRI_DATA/nyspi/' + project_id
    rawdata_path = project_path + '/rawdata'
    bidsonly_path = project_path + '/derivatives/bidsonly'
    working_list_file = project_id + '_working.lst'
    working_list_path = project_path + '/scripts/' + working_list_file

    #............................................................
    #   working.lst ARGUMENT PARSER
    #   copy & paste anywhere for working.lst parsing in python
    #............................................................

    encrypted_file_path = project_path + '/.tokens/xnat2bids_' + project_id + '_login.bin'

    print("\nencrypted_file_path : ")
    print(encrypted_file_path)

    with open(encrypted_file_path, "rb") as encrypted_file:
            
        print("\nencrypted_file : ")
        print(encrypted_file)

        private_key_path = project_path + '/.tokens/xnat2bids_private.pem'
        private_key = RSA.import_key(open(private_key_path).read())

        print("\nprivate_key: ")
        print(private_key)

        encrypted_session_key, nonce, tag, ciphertext = \
            [ encrypted_file.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

        # Decrypt session key with private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(encrypted_session_key)

        # Decrypt the password with AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        password = cipher_aes.decrypt_and_verify(ciphertext, tag)

    if len(password) > 0:
        # Remove this for production!
        print("Decoded message: " + password.decode("utf-8"))
        xnat_password = str(password.decode("utf-8")).strip()
    else:
        print("Could not retrieve xnat login password")


    #............................................................
    #   working.lst ARGUMENT PARSER
    #   copy & paste anywhere for working.lst parsing in python
    #............................................................
    
    print('Trying to read from working list path: ' + working_list_path)
    print('Time to access file could depend on /MRI_DATA i/o load...')

    with open(working_list_path) as f:
        jobs = f.readlines()

    download_queue = []
    active_job_no = 0
    total_jobs=len(jobs)
    print("\n" + str(total_jobs) + " jobs found in working list.\n")

    # Pull just exam numbers from working list. It's all we need.
    for job in jobs:
        
        print(job)

        # working.lst format: <subj_id> '\t' <project_id> '\t' <exam_no> '\t' XNATnyspi20_E00253
        exam_no = job.split()[2]
        print("Grabbing " + exam_no + " as exam number")
        download_queue.append(exam_no)

    #............................................................
    #   END COPY & PASTE (continue indent for loop above)
    #............................................................

#............................................................
#             AUTHENTICATION: alias k:v tokens, then jsession token
#   copy & paste anywhere for JSESSION retrieval block
#............................................................
    
    # TODO: fix this
    
    #.....................................................
    #   1st session: request alias tokens (48hr life)
    #.....................................................
    
    xnat_username = 'grayjoh'

    xnat_url = 'https://xnat.nyspi.org'
    alias_token_url_user = xnat_url + '/data/services/tokens/issue'
    alias_token_url_admin = alias_token_url_user + '/user/' + xnat_username

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
    print("generated single-use alias :" + alias)
    print("generated single-use secret :" + secret)

# TODO: figure out how to close this session

    #.....................................................
    #   2nd session: use the alias tokens to request JSESSION token
    #.....................................................
    jsession_url = xnat_url + '/data/JSESSION'
    session = requests.Session()    # Stores all the info we need for our session
    session.auth = (alias, secret)
    jsession_id = session.post(jsession_url)

    # Put JSESSION auth ID returned by XNAT rest api inside cookies header
    # Now only the JSESSION ID is available to headers,
    # No XNAT username or password is stored
    session.text = {
        "cookies":
        {
            "JSESSIONID": jsession_id.text
        }
    }

    resources = 'BIDS,NIFTI'

    session_list_url = xnat_url + '/data/archive/projects/' + project_id + '/experiments?xsiType=xnat:mrSessionData&format=csv&columns=ID,label,xnat:subjectData/label'

    #................................................
    #...........GET SESSION LIST.....................
    #................................................
    dt = datetime.datetime.now()
    year_month_day = str(dt.year) + str(dt.month) + str(dt.day)
    session_list_csv = bidsonly_path + '/XNAT_metadata/mrsessions_' + year_month_day + '.csv'
    print('Checking for mrsessions.csv file (should be in ' + bidsonly_path + ')...')
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
            print("Writing file (this could take some time)...")
            # download in chunks to save buffer memory on doctor
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)
                # print("~~ writing chunks ~~~")
    #................................................
    #...........END GET SESSION LIST.................
    #................................................


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
        print("Pulled info on " + str(len(lines)) + " sessions.")
        mrsession_ids = []

        for line in lines:
            
            args = job.split()
            arg_no = 0

            label = line.split(',')[-2]
            labels.append(label)
            # mrsession_id = line.split(',')[0]
            # mrsession_ids.append(mrsession_id)

            # Pull accession_no from list of project sessions if exam number
            # matches input args and only download those exams
            print('Scanning list for requested exams...')
            if label in download_queue:
                print('Found exam ' + str(label) + '. Downloading...')

                print("Args for job " + str(active_job_no) + ' of ' + str(total_jobs) + ": " )
                print(*args)
                print("\n")

                bidsonly_exam_path = bidsonly_path + label
            
                mrsession_id = line.split(',')[0]
                mrsession_ids.append(mrsession_id)
                scan_download_url = str(xnat_url + '/data/experiments/' + mrsession_id + '/scans/ALL/resources/' + resources + '/files?format=zip&structure=legacy')
                unzipped_path = bidsonly_path + '/' + label
                zipfile = label + '.zip'
                zipfile_path = bidsonly_path + '/' + zipfile

                print('Entering scan download stage...')
    # IF EXAM FOLDER EXISTS DO NOT WRITE
    # TODO: Implement checksums to patch missing data seamlessly
                if not os.path.exists(unzipped_path):
                    try:
                        print("Creating directory structure for " + zipfile)
                        os.makedirs(os.path.dirname(zipfile_path))
                    except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            raise
                else:
                    print(unzipped_path + "\nDirectory exists for " + exam_no + ". Moving to next exam in working list.")
                    continue
    # WRITE ZIPFILE OF CURRENT SCAN
                with open(zipfile_path, 'wb') as f:
                    print("Opening file to write response contents to...")
                    with session.get(scan_download_url, stream=True) as r:

                        print("Checking status...")
                        if not r.raise_for_status():
                            print("no status raised (good)")
                        print("Attempting to write file...")
                        chunk_size = 256000000 # 256mb                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            f.write(chunk)
                            print("~~ writing " + str(chunk_size) + "kb chunks ~~~")
                    # Put close session command here
                        
                        # Alternatively, we can use subprocess.popen() to call
                        # a shell command, like rsync
                    # p = Popen(["nohup", "rsync", "-bwlimit=10000", "" scan_download_url])

                print("Download complete. Attempting to unzip " + zipfile_path)
                try:
                    with ZipFile(zipfile_path, 'r') as zipObj:
                        zipObj.extractall(bidsonly_path)
                except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            raise

                if os.path.isdir(bidsonly_path + '/' + exam_no):
                    print("File unzipped. Check " + bidsonly_path)
                else:
                    print("There was a problem and we were unable to extract the downloaded files. Check if the download completed successfully.")

    #................................................
    #..............END XNAT DOWNLOAD.................
    #................................................

if __name__ == '__main__':
    download_niftis(project_id)