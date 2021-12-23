import os 

from download import download
from unzip import unzip
# from download_exam import session
import setup

def download_niftis(mrsession_id, session):
    print("Writing NIFTI files...")
    scan_download_url = setup.scan_download_url(mrsession_id)
    
    # DOWNLOAD NIFTI + JSON DATA
    # TODO: grab REAL file size
    min_exam_size = 900*1000000
    min_exam_mb = min_exam_size/1000000
    if not os.path.exists(os.path.dirname(setup.zipfile_path)): # check if unzipped archive exists already
        print("Folder already exists in this directory matching this name.")

    elif os.path.exists(setup.zipfile_path):  # Make sure zipfile wasn't already downloaded
        print('Detected existing zipfile for this scan. Trying to unzip.')
        try:
            unzip(zipfile_path=setup.zipfile_path) # see if it can be unzipped 
        except:
            print("Could not unzip " + setup.zipfile_path + ". Archive may be incomplete. Attempting to re-download...")
            download(session=session, url=scan_download_url, path=setup.zipfile_path, chunk_size=100*1000000) # download max of 100mb chunks

    else:
        try:    # attempt download if the archive is corrupt or incomplete
            download(session=session, url=scan_download_url, path=setup.zipfile_path, chunk_size=100*1000000) # download max of 100mb chunks
        except OSError as exc:
            print("There was a problem downloading the exam archive.")
            if exc.errno != errno.EEXIST:
                raise
                                
    try:
        unzip(zipfile_path=setup.zipfile_path)
    except:
        print("Could not unzip " + setup.zipfile_path + ". Moving on.")
        pass