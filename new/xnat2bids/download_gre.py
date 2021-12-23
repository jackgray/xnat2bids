
import setup
import os


def download_gre(mrsession_id, session)
# CHECK FOR NEUROMELANIN DICOMS
    # print(mrScanData.text)
    scan_info_json = loads(mrScanData)['ResultSet']['Result']
    nm_download_urls = []
    print("Checking this exam for neuromelanin data...")
    for i in scan_info_json:
        series_description=i['series_description']
        if 'gre' in series_description:
            nm_scan_no = i['URI'].split('/')[-1]    # pull series number from rest download path
            nm_download_url = setup.nm_download_url(mrsession_id, nm_scan_no)
            nm_zipfile_path = setup.bidsonly_path + '/neuromelanin_dicoms_' + nm_scan_no + '.zip'
            print("Found neuromelanin scan to download. Downloading to " + nm_zipfile_path + '...')
            min_nm_filesize = 8*1000000
            min_nm_mb=min_nm_filesize/1000000
            if os.path.exists(nm_zipfile_path) and os.path.getsize(nm_zipfile_path) < min_nm_filesize: # 8mb
                print("File already exists but may not be complete (less than " + min_nm_mb + " mb. Downloading again.")
                download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=10*1000000)
            elif os.path.exists(nm_zipfile_path):
                print("Looks like this file was already downloaded. Let's try to unzip it")
            else:
                try:
                    download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=10*1000000)
                except:
                    print("There was a problem downloading " + nm_zipfile_path)
                    break
            try:
                unzip(zipfile_path=nm_zipfile_path)
            except:
                print("Unable to unzip " + nm_zipfile_path + '. Attempting to re-download.')
                try:
                    download(session=session, url=nm_download_url,path=nm_zipfile_path, chunk_size=1000000)
                except:
                    print("There was a problem downloading " + nm_zipfile_path)
                    pass
                try:
                    unzip(zipfile_path=nm_zipfile_path)
                except:
                    print("Still couldn't unzip " + nm_zipfile_path)
