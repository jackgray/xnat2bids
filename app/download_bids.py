import os 
import errno

from download import download
from unzip import unzip
import setup

def download_bids(mrsession_id, session, exam_no):
    print("Writing NIFTI files...")
    scan_download_url = setup.scan_download_url(mrsession_id)
    
    exam_path = '/bidsonly/' + exam_no
    zipfile_path = str(exam_path) + '.zip'
    
    # TODO: grab REAL file size from XNAT API
    if os.path.exists(zipfile_path):  # Make sure zipfile wasn't already downloaded
        print('\nDetected existing zipfile for this scan at', zipfile_path, '. Trying to unzip.')
        try:
            unzip(zipfile_path) # see if it can be unzipped 
        except:
            print("\n!!! Could not unzip ", zipfile_path, ". Archive may be incomplete. Attempting to re-download...")
            download(session=session, url=scan_download_url, path=zipfile_path, chunk_size=setup.nifti_chunk_size) # download max of 100mb chunks
            print("Download of ", zipfile_path, " complete. \nUnzipping archive...")
            unzip(zipfile_path)
    else:
        try:    # attempt download if the archive is corrupt or incomplete
            download(session=session, url=scan_download_url, path=zipfile_path, chunk_size=setup.nifti_chunk_size) 
            print("Attempting to unzip...")
            try:
                unzip(zipfile_path)
            except:
                print("\n!!! Could not unzip " + zipfile_path + ". Moving on.")
                pass
        except OSError as exc:
            print("!!! There was a problem downloading the exam archive.")
            if exc.errno != errno.EEXIST:
                raise
                                
    