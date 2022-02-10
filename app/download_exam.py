# Py modules
from os import path
from time import sleep

# Dev modules
from login import xnat_login
from download_bids import download_bids
from download_by_name import download_keyword, download_nm, download_me, download_keyword
from download import download
from organize import move2raw
import constants


def download_exam(exam_no, action):
    
    print("\n******* Entering download stage for exam ", exam_no, " *******")
     
    session = xnat_login(encrypted_alias_path=constants.encrypted_alias_path)
    
    # GET SESSION CSV - Retrieve list of all exams for the project from XNAT
    session_list_csv_path = constants.session_list_csv_path()
    try:    # Open if one was already downloaded for today, otherwise download a new one
        with open(session_list_csv_path, 'r') as f:
            print("\nFound session csv file from earlier today. Reading and parsing it...")
            lines = f.readlines()
            if lines.startswith('<'):   # indicates html header response
                print("Could not retrieve any scans from the file. Deleting and requesting a new one.")
                raise
    except:
        print("\nNo recent session manifest found. Trying to download updated version.")
        download(session=session, url=constants.session_list_url, path=session_list_csv_path, chunk_size=constants.text_chunk_size)
        with open(session_list_csv_path, 'r') as f:
            print("\nReading and parsing session manifest file.")
            lines = f.readlines()
    lines.pop(0)    # Remove 1st line of column labels as they are not exams
    labels = []
    print("\nPulled info on " + str(len(lines)) + " sessions. Looking for exams matching ", exam_no)

    mrsession_ids = []
    # Compare working.lst to session manifest csv
    for line in lines:  # a row in session list csv file. each row is one session. 
        label = line.split(',')[-2] # Label = Exam no; third column in csv 
        # If there's a match, pull its mr accession no. from its neighboring column
        if label == exam_no:      
            print('\nFound accession no. for exam ' + str(label) + " on XNAT. Checking that the data doesn't already exist. If not, we'll try to download it.")
            mrsession_id = line.split(',')[0]
            subject_id = line.split(',')[2]
            print(" Using MR Session ID: " + mrsession_id + " to download exam " + exam_no + " from XNAT.")
            # Get session info (series descriptions) & corresponding scan(series) numbers for nm dicom data organization
            mrScanData = session.get(constants.scan_list_url(mrsession_id)).text

            print("\nRunning download mode: ", action)  # nm, bids, or ll
            # DOWNLOAD NIFTI + JSON DATA
            if action.endswith('bids'):
                print("\nDownloading bids data (NIFTI + JSON)")
                download_bids(mrsession_id, session, exam_no)
            
            # DOWNLOAD NM DATA
            elif action.endswith('nm'):
                download_nm(mrsession_id, session, mrScanData, exam_no)
            elif action.endswith('me'):
                print("\nComing soon! Downloading multi-echo data.")
                download_me(mrsession_id, session, mrScanData, exam_no)

            # KEYWORD DOWNLOAD 
            elif action.endswith('custom'):
                print("\nWARNING! Experimental Feature: We'll try to download specific scans for your exam that match your input criteria.")
                from constants import keywords, excludes
                download_keyword(mrsession_id, session, mrScanData, exam_no, keywords, excludes)

            # DOWNLOAD ALL 
            else:
                print("\nDownloading all available data for the exam.")
                download_bids(mrsession_id, session, exam_no)
                download_nm(mrsession_id, session, mrScanData, exam_no)
            # Sort data after checking that it was downloaded
            if path.exists(constants.exam_path(exam_no)):
                print("\nFinished download for ", exam_no, " entering sorting mode...")
                move2raw(exam_no, subject_id)
            else:
                print("\nNo data was downloaded for ", exam_no, ". Check that you are requesting data that exists or that your working.lst file is populated.")
        
    print("\nExiting.")
    sleep(5)    # Sleep long enough for docker service to verify to avoid false failure on quick downloads