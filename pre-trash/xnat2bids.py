#!/pythonlibs python3
'''
usage: python3 index.py <project ID>

This program is designed to take the project_id as single argument
which points to the working.lst for that project.

It will 
1. Pass command line args of this script to dn_nifti.py
and execute to download all NIFTI and JSON data specified in 
the <project ID>_working.lst file.

2. When scans are finished downloading, nifti2bids will run with
the same arguments being passed from this script.

OR run each script individually in the same way by specifying project ID
as an input argument.
'''

import dn_nifti
import nifti2bids
from os import environ as env

# import argparse

# parser = argparse.ArgumentParser(description='Download output of dcm2bids from XNAT.')
# parser.add_argument("project_id")
# args = parser.parse_args()

# project_id = args.project_id

project_id = env['project_id']

def xnat2bids(project_id):
    dn_nifti.download_niftis(project_id)
    nifti2bids.nifti2bids(project_id)

if __name__ == '__main__':
    xnat2bids(project_id)