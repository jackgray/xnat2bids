from os import environ, stat
from datetime import datetime

# Pass arguments as env vars from service launch script
project_id = 'spanint'
# environ['project_id']
exam_no = str('19801')
#str(environ['single_exam_no'])
username = 'grayjoh'
#environ['username']
uid = stat('/home/jackgray').st_uid
#= environ[uid]
gid = -1  
#= environ[gid]

# XNAT rest api vars
nifti_resources = 'BIDS,NIFTI'
nm_resources = 'DICOM'


# URL defs (XNAT rest api)
xnat_url = 'https://xnat.nyspi.org'
alias_token_url = xnat_url + '/data/services/tokens/issue'
jsession_url = xnat_url + '/data/JSESSION'
# GETs
session_list_url = xnat_url + '/data/archive/projects/' + project_id + '/experiments?xsiType=xnat:mrSessionData&format=csv&columns=ID,label,xnat:subjectData/label'
def scan_list_url(mrsession_id):
    scan_list_url = xnat_url + '/data/experiments/' + mrsession_id + '/scans'
    return scan_list_url
def scan_download_url(mrsession_id):
    scan_download_url = xnat_url + '/data/experiments/' + mrsession_id + '/scans/ALL/resources/' + nifti_resources + '/files?format=zip'
    return scan_download_url
def nm_download_url(mrsession_id, nm_scan_no):
    nm_download_url = xnat_url + '/data/experiments/' + mrsession_id + '/scans/' + nm_scan_no + '/resources/' + nm_resources + '/files?format=zip'
    return nm_download_url

# Container Path defs
project_path = '/MRI_DATA/nyspi/' + project_id
bidsonly_path = '/bidsonly'
exam_path = bidsonly_path + '/' + exam_no
rawdata_path = '/rawdata'

def session_list_csv_path():
    dt = datetime.now()
    year_month_day = str(dt.year) + str(dt.month) + str(dt.day)
    session_list_csv_path = bidsonly_path + '/XNAT_metadata/mrsessions_' + year_month_day + '.csv'
    print("\nChecking for mrsessions.csv file (should be in " + bidsonly_path + ')...')
    print('If it doesn\'t exist, we will attempt to download it.')
    return session_list_csv_path

zipfile = exam_no + '.zip'    # label and exam_no are the same
zipfile_path = exam_path + '.zip'
token_path = '/tokens'
token_filename = 'xnat2bids_' + username + '_login.bin'
encrypted_token_path = token_path + '/xnat2bids_' + username + '_login.bin'
encrypted_alias_path = token_path + '/xnat_alias_' + username + '.bin'
private_key_path = "/xnat/xnat2bids_private.pem"
public_key_path = "/app/xnat2bids_public.pem"

# TODO: Add option for interactive path defs on failed attempts

