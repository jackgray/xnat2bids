from os import environ, stat, path
# from os.path import join
from datetime import datetime

# Pass arguments as env vars from service launch script
project_id = environ['project_id']
exam_no = str(environ['exam_no'])
username = environ['username']
uid = int(environ['uid'])
gid = int(environ['gid'])
action=environ['action']
department = environ['department']
host=environ['host']

if len(action) > 1:
    action = environ['action'] # ex. 'dl-bids' or 'dl_nm' or dl_all
else:
    action = 'dl_all'

# XNAT rest api vars
nifti_resources = 'BIDS,NIFTI'
nm_resources = 'DICOM'
dicom_chunk_size = 100000000  # 100mb
nifti_chunk_size = 100000000 # 100 mb
text_chunk_size = 512000 #  512 kb


# URL defs (XNAT rest api)
if not len(host) > 1:  
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
project_path = path.join('/MRI_DATA', department, project_id)
working_list_path = '/scripts/' + project_id + '_working.lst'
bidsonly_path = '/bidsonly'
def exam_path(exam_no):
    exam_path = path.join(bidsonly_path, exam_no)
    return exam_path
rawdata_path = '/rawdata'


def session_list_csv_path():
    dt = datetime.now()
    year_month_day = str(dt.year) + str(dt.month) + str(dt.day)
    session_list_csv_path = bidsonly_path + '/XNAT_metadata/mrsessions_' + year_month_day + '.csv'
    print("\nChecking for mrsessions.csv file (should be in " + bidsonly_path + ')...')
    print('If it doesn\'t exist, we will attempt to download it.')
    return session_list_csv_path


token_path = '/tokens'
token_filename = 'xnat2bids_' + username + '_login.bin'
encrypted_token_path = token_path + '/xnat2bids_' + username + '_login.bin'
encrypted_alias_path = token_path + '/xnat_alias_' + username + '.bin'
private_key_path = "/xnat/xnat2bids_private.pem"
public_key_path = "/public_token/xnat2bids_public.pem"

# TODO: Add option for interactive path defs on failed attempts

bidsmap_path = rawdata_path + '/bidsmap_' + project_id + '.json'
dcm2bids_path = rawdata_path + '/d2b-template_'+ project_id + '.json'


def get_exams():
    if len(exam_no) > 1:
        print("\nDetected single exam mode. Downloading ", exam_no)
        exams = str(exam_no.strip())
    else:
        with open(working_list_path) as working_list:
            exams = working_list.readlines()
    return exams

