
import setup
import os
from json import loads

from download import download
from unzip import unzip
from setup import dicom_chunk_size, exam_path

def download_nm(mrsession_id, session, mrScanData, exam_no):
    exam_path = '/bidsonly/' + exam_no
    # CHECK FOR NEUROMELANIN DICOMS
    scan_info_json = loads(mrScanData)['ResultSet']['Result']
    nm_download_urls = []
    print("\nChecking this exam for neuromelanin data...")
    
    for i in scan_info_json:
        series_description=i['series_description']
        
        if 'gre' in series_description:
            nm_scan_no = i['URI'].split('/')[-1]    # pull series number from supplied rest api download path
            nm_download_url = setup.nm_download_url(mrsession_id, nm_scan_no)
            nm_zipfile_path = os.path.join(setup.bidsonly_path, nm_scan_no + "-" + series_description) + '.zip'    
            nm_unzip_path = os.path.join(exam_path, "scans", nm_scan_no + "-" + series_description)
            
            if os.path.exists(nm_zipfile_path):
                print("Looks like this file was already downloaded. Let's try to unzip it.")
                try:
                    unzip(zipfile_path=nm_zipfile_path)
                except:
                    print("Unable to unzip " + nm_zipfile_path + '. Attempting re-download.')
                    download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=setup.dicom_chunk_size)
                    try:
                        unzip(zipfile_path=nm_zipfile_path)
                    except:
                        print("Still couldn't unzip " + nm_zipfile_path + "\n Delete the contents of /bidsonly and try again. Contact a member of the computing team if this problem persists.")
            else:
                print("\n\nFound neuromelanin scan to download. Downloading to " + nm_zipfile_path + '...')
                download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=setup.dicom_chunk_size)
                try:
                    unzip(zipfile_path=nm_zipfile_path)
                except:
                    print("Unable to unzip " + nm_zipfile_path + '. Attempting re-download.')
                    
                    download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=setup.dicom_chunk_size)
                    try:
                        unzip(zipfile_path=nm_zipfile_path)
                    except:
                        print("Still couldn't unzip " + nm_zipfile_path)
