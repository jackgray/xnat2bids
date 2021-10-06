import dn_nifti
import nifti2bids


import argparse

parser = argparse.ArgumentParser(description='Download output of dcm2bids from XNAT.')
parser.add_argument("project_id")
args = parser.parse_args()

project_id = args.project_id

def xnat2bids(project_id):
    dn_nifti.download_niftis(project_id)
    nifti2bids.nifti2bids(project_id)

if __name__ == '__main__':
    xnat2bids(project_id)