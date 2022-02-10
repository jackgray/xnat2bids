import os
from json import loads

import constants
from download import download
from unzip import unzip
from fix_perms import fix_perms

def download_nm(mrsession_id, session, mrScanData, exam_no):
    exam_path = '/bidsonly/' + exam_no
    # CHECK FOR NEUROMELANIN DICOMS
    scan_info_json = loads(mrScanData)['ResultSet']['Result']
    nm_download_urls = []
    print("\nChecking this exam for neuromelanin data...")
    
    for i in scan_info_json:
        series_description=i['series_description'].lower()
        
        if 'gre' in series_description and not 'me' in series_description and not 'loc' in series_description:
            nm_scan_no = i['URI'].split('/')[-1]    # pull series number from supplied rest api download path
            nm_download_url = constants.nm_download_url(mrsession_id, nm_scan_no)
            nm_zipfile_path = constants.nm_zipfile_path(exam_no, series_description, nm_scan_no)   
            nm_unzip_path = os.path.join(exam_path, "scans", nm_scan_no + "-" + series_description)

            print("\n\nFound neuromelanin scan to download. Downloading to " + nm_zipfile_path + '...')
            download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=constants.dicom_chunk_size)
            fix_perms(nm_zipfile_path)

    print("\nFinished neuromelanin downloads")

# Download Multi-Echo scans
def download_me(mrsession_id, session, mrScanData, exam_no):
    exam_path = '/bidsonly/' + exam_no
    # CHECK FOR NEUROMELANIN DICOMS
    scan_info_json = loads(mrScanData)['ResultSet']['Result']
    nm_download_urls = []
    print("\nChecking this exam for multi-echo data...")
    
    for i in scan_info_json:
        series_description=i['series_description'].lower()  # Normalize lettercase
        
        if 'me' in series_description and not 'gre' in series_description:
            nm_scan_no = i['URI'].split('/')[-1]    # pull series number from supplied rest api download path
            nm_download_url = constants.nm_download_url(mrsession_id, nm_scan_no)
            nm_zipfile_path = constants.nm_zipfile_path(exam_no, series_description, nm_scan_no)   
            nm_unzip_path = os.path.join(exam_path, "scans", nm_scan_no + "-" + series_description)

            print("\n\nFound neuromelanin scan. Downloading to " + nm_zipfile_path + '...')
            download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=constants.dicom_chunk_size)
            fix_perms(nm_zipfile_path)

    print("\nFinished multi-echo downloads")

# Download user defined scans by keyword
def download_keyword(mrsession_id, session, mrScanData, exam_no, keywords, excludes):
    exam_path = '/bidsonly/' + exam_no
    # CHECK FOR NEUROMELANIN DICOMS
    scan_info_json = loads(mrScanData)['ResultSet']['Result']
    nm_download_urls = []
    print("\nChecking this exam for data matching user input criteria...")
    
    for scan in scan_info_json:
        series_description=scan['series_description'].lower()  # Normalize lettercase
        print("\nChecking ", series_description, " for match.")
        
        keyword_list = [x.strip(' ') for x in keywords.split(',')]
        print("Including: ", *keyword_list)
        
        exclude_list = [x.strip(' ') for x in excludes.split(',')]
        print("Excluding: ", *exclude_list)

        if all(x in series_description for x in keyword_list) and not any(x in series_description for x in exclude_list):
            nm_scan_no = scan['URI'].split('/')[-1]    # pull series number from supplied rest api download path
            nm_download_url = constants.nm_download_url(mrsession_id, nm_scan_no)
            nm_zipfile_path = constants.nm_zipfile_path(exam_no, series_description, nm_scan_no)   
            nm_unzip_path = os.path.join(exam_path, "scans", nm_scan_no + "-" + series_description)

            print("\n\nFound matching scan to download. Downloading to " + nm_zipfile_path + '...')
            download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=constants.dicom_chunk_size)
            fix_perms(exam_path)

    print("\nFinished pulling scans for exam ", exam_no, " matching the keywords [", *keyword_list, "] but excluding [", *exclude_list, "]")


# FOR UNZIPPING, replace print, download, and fix_perms (lns 25-27) with this block
            # if os.path.exists(nm_zipfile_path):
            #     print("Looks like this file was already downloaded. Let's try to unzip it.")
            #     try:
            #         unzip(zipfile_path=nm_zipfile_path)
            #     except:
            #         print("Unable to unzip " + nm_zipfile_path + '. Attempting re-download.')
            #         download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=constants.dicom_chunk_size)
            #         try:
            #             unzip(zipfile_path=nm_zipfile_path)
            #         except:
            #             print("Still couldn't unzip " + nm_zipfile_path + "\n Delete the contents of /bidsonly and try again. Contact a member of the computing team if this problem persists.")
            # else:
            #     print("\n\nFound neuromelanin scan to download. Downloading to " + nm_zipfile_path + '...')
            #     download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=constants.dicom_chunk_size)
            #     fix_perms(nm_zipfile_path)
            #     try:
            #         unzip(zipfile_path=nm_zipfile_path)
            #     except:
            #         print("Unable to unzip " + nm_zipfile_path + '. Attempting re-download.')
                    
            #         download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=constants.dicom_chunk_size)
            #         try:
            #             unzip(zipfile_path=nm_zipfile_path)
            #         except:
            #             print("Still couldn't unzip " + nm_zipfile_path)
