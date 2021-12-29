'''
handles password and keyfile generation
 -- will prompt user to re-enter auth process (separate container)
    if session fails.
'''

# REQUIRES: setup.py, login.py unzip.py fix_perms.py download.py

from login import login
from download_bids import download_bids
from download_nm import download_nm
from download import download
from organize import move2raw

import setup


def download_exam(exam_no, action):
    
    print("*************Entering download stage for exam ", exam_no, " ***************************")
    
    # Create session / get JSESSION token if JSESSION wasn't passed in environment
    session = login(encrypted_alias_path=setup.encrypted_alias_path)
    
    # GET SESSION CSV - Retrieve list of all exams for the project from XNAT
    session_list_csv_path = setup.session_list_csv_path()
    print("\nRetrieving session list for " + setup.project_id + " from XNAT")
    try:    # Open if one was already downloaded for today, otherwise download a new one
        with open(session_list_csv_path, 'r') as f:
            print("\nFound session csv file from earlier today. Reading and parsing it...")
            lines = f.readlines()
    except:
        print("\nNo recent session manifest found. Trying to download updated version.")
        download(session=session, url=setup.session_list_url, path=session_list_csv_path, chunk_size=setup.text_chunk_size)
        with open(session_list_csv_path, 'r') as f:
            print("\nReading and parsing session manifest file.")
            lines = f.readlines()
    lines.pop(0)    # Remove 1st line of column labels as they are not exams
    labels = []
    print("\nPulled info on " + str(len(lines)) + " sessions.")
    mrsession_ids = []

    # COMPARE WORKING.LST TO SESSION CSV
    for line in lines:  # a row in session list csv file. each row is one session. 
        label = line.split(',')[-2] # Label = Exam no; third column in csv 
        # If there's a match, pull its mr accession no. from its neighboring column
        if label == exam_no:      
            print('\nFound accession no. for exam ' + str(label) + " on XNAT. Checking that the data doesn't already exist. If not, we'll try to download it.\n")
            mrsession_id = line.split(',')[0]
            subject_id = line.split(',')[2]
            print("Using MR Session ID: " + mrsession_id + " to download exam " + exam_no + " from XNAT.")
            
            ## GET SESSION INFO AKA SERIES DESCRIPTIONS AND CORRESPONDING SCAN(SERIES) NUMBERS (for nm dicom data organization)
            mrScanData = session.get(setup.scan_list_url(mrsession_id)).text

            print("\n\n\nRunning download mode: ", action)  # dl_nm, dl_bids, or dl_all
            # DOWNLOAD NIFTI + JSON DATA
            if action.endswith('bids') or action.endswith('all'):
                print("\nDownloading bids data (NIFTI + JSON)")
                download_bids(mrsession_id, session, exam_no)
            # DOWNLOAD NM DATA
            elif action.endswith('nm') or action.endswith('all'):
                print("\nDownloading neuromelanin data as DICOMs")
                download_nm(mrsession_id, session, mrScanData, exam_no)
            # DOWNLOAD ALL 
            else:
                print("\nDidn't detect which scans you want, so I'm downloading the entire exam.")
                download_bids(mrsession_id, session, exam_no, subject_id)
                download_nm(mrsession_id, session, mrScanData, exam_no, subject_id)
      
            print("\n\nDOWNLOAD  OF EXAM ", exam_no, " COMPLETE\n\n\n")
            
            move2raw(exam_no, subject_id)