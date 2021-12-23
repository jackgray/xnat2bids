'''
handles password and keyfile generation
 -- will prompt user to re-enter auth process (separate container)
    if session fails.
'''

# REQUIRES: setup.py, login.py unzip.py fix_perms.py download.py

import os, stat
import errno
import requests
import datetime
from json import loads, dumps
from shutil import rmtree
from zipfile import ZipFile
from subprocess import Popen
from collections import Counter

from login import login
from download_niftis import download_niftis
from download import download
from unzip import unzip
from fix_perms import fix_perms
import setup

def download_exam(exam):
    # Create session / get JSESSION token
    session = login(encrypted_alias_path=setup.encrypted_alias_path)
    print(session.text)
    # Retrieve list of all exams for the project from XNAT
    # Create directory for session list csv file
    session_list_csv_path = setup.session_list_csv_path()
    # if not os.path.exists(os.path.dirname(session_list_csv_path)):
    #     try:
    #         print("Creating directory structure for " + session_list_csv_path.split('/')[-1])
    #         os.makedirs(os.path.dirname(session_list_csv_path))
    #     except OSError as exc:
    #         if exc.errno != errno.EEXIST:
    #             raise
    
    # First lets check and make sure the file wasn't already downloaded

    # Download session list csv from XNAT
    try:
        print("Retrieving session list for " + setup.project_id + " from XNAT")
        download(session=session, url=setup.session_list_url, path=setup.session_list_csv_path(), chunk_size=128000)
    except:
        print("There was an error downloading sessions csv file. Check download function and JSESSION generation.")
        pass
    #................................................
    #...........DOWNLOAD SCANS FROM XNAT.............
    #................................................
    # Read mrsession csv and extract labels
    # Scans will ultimately be downloaded by their session label
    print(os.path.dirname(session_list_csv_path))
    if not os.path.exists(os.path.dirname(session_list_csv_path)):
        print("Creating path for XNAT metadata")
        os.makedirs(os.path.dirname(session_list_csv_path))
    with open (session_list_csv_path, 'r') as f:
        print("Reading and parsing session csv file...")
        lines = f.readlines()
    lines.pop(0)    # Remove 1st line of column labels as they are not exams
    labels = []
    print("\nPulled info on " + str(len(lines)) + " sessions.")
    mrsession_ids = []

    # label: what the xnat csv calls an exam number -- label=exam_no
    for line in lines:  # a row in session list csv file. each row is one session. 
        label = line.split(',')[-2]
        # Compare exam input arg to xnat manifest
        # If there's a match, pull it's mr accession no. from it neighboring column
        if label == exam:
            print('\nFound accession no. for exam ' + str(label) + " on XNAT. Checking that the data doesn't already exist. If not, we'll try to download it using these input arguments...\n")
            mrsession_id = line.split(',')[0]
            print("Using MR Session ID: " + mrsession_id + " to download exam " + exam + " from XNAT.")
            
            ## GET SESSION INFO AKA SERIES DESCRIPTIONS AND CORRESPONDING SCAN(SERIES) NUMBERS
            mrScanData = session.get(setup.scan_list_url(mrsession_id)).text

            # WRITE ALL NIFTI AND JSON INTO ZIPFILE 
            download_niftis(mrsession_id, session)

            # CHECK FOR NEUROMELANIN DICOMS
            # print(mrScanData.text)
            scan_info_json = loads(mrScanData)['ResultSet']['Result']
            nm_download_urls = []
            print("Checking this exam for neuromelanin data...")
            for i in scan_info_json:
                series_description=i['series_description']
                if 'gre' in series_description:
                    nm_scan_no = i['URI'].split('/')[-1]    # pull series number from rest download path
                    nm_download_url = setup.nm_download_url(mrsession_id, nm_scan_no)
                    nm_zipfile_path = setup.bidsonly_path + '/neuromelanin_dicoms_' + nm_scan_no + '.zip'
                    print("Found neuromelanin scan to download. Downloading to " + nm_zipfile_path + '...')
                    min_nm_filesize = 8*1000000
                    min_nm_mb=min_nm_filesize/1000000
                    if os.path.exists(nm_zipfile_path) and os.path.getsize(nm_zipfile_path) < min_nm_filesize: # 8mb
                        print("File already exists but may not be complete (less than " + min_nm_mb + " mb. Downloading again.")
                        download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=10*1000000)
                    elif os.path.exists(nm_zipfile_path):
                        print("Looks like this file was already downloaded. Let's try to unzip it")
                    else:
                        try:
                            download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=10*1000000)
                        except:
                            print("There was a problem downloading " + nm_zipfile_path)
                            break
                    try:
                        unzip(zipfile_path=nm_zipfile_path)
                    except:
                        print("Unable to unzip " + nm_zipfile_path + '. Attempting to re-download.')
                        try:
                            download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=1000000)
                        except:
                            print("There was a problem downloading " + nm_zipfile_path)
                            pass
                        try:
                            unzip(zipfile_path=nm_zipfile_path)
                        except:
                            print("Still couldn't unzip " + nm_zipfile_path)

    print("\n\n\nFIN!\n\n\n")