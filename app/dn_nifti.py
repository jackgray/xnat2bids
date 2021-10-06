'''
This program is designed to take the project_id as single argument
which points to the working.lst for that project.
'''
def download_niftis(project_id):

    print('Check if there is a project id ')
    print('Project ID: ' + project_id)

    import os
    import errno
    import requests
    import datetime
    import getpass
    from zipfile import ZipFile

    #............................................................
    #   working.lst ARGUMENT PARSER
    #   copy & paste anywhere for working.lst parsing in python
    #............................................................
    if not project_id:
        import argparse

        parser = argparse.ArgumentParser(description='Download output of dcm2bids from XNAT.')
        parser.add_argument("project_id")
        args = parser.parse_args()

        project_id = args.project_id
    
    project_path = '/MRI_DATA/nyspi/' + project_id
    rawdata_path = project_path + '/rawdata'
    bidsonly_path = project_path + '/derivatives/bidsonly'
    working_list_file = project_id + '_working.lst'
    working_list_path = project_path + '/scripts/' + working_list_file

    with open(working_list_path) as f:
        jobs = f.readlines()

    download_queue = []
    active_job_no = 0
    total_jobs=len(jobs)
    print("\n" + str(total_jobs) + " jobs found in working list.\n")

    # Pull just exam numbers from working list. It's all we need.
    for job in jobs:
        
        print(job)

        # working.lst format: <subj_id> '\t' <project_id> '\t' <exam_no> '\t' XNATnyspi20_E00253
        exam_no = job.split()[2]
        print("Grabbing " + exam_no + " as exam number")
        download_queue.append(exam_no)

    #............................................................
    #   END COPY & PASTE (continue indent for loop above)
    #............................................................

    # sh = hashlib.sha1()
    # sh.update('dnniftinyspidoctor')
    print("\nLog into XNAT to download data: ")
    xnat_username = input('Username: ')
    xnat_password = getpass.getpass()

    xnat_url = 'https://xnat.nyspi.org'
    jsession_url = xnat_url + '/data/JSESSION'

    resources = 'BIDS,NIFTI'

    session_list_url = xnat_url + '/data/archive/projects/' + project_id + '/experiments?xsiType=xnat:mrSessionData&format=csv&columns=ID,label,xnat:subjectData/label'
    # bids_resource_url = xnat_url + '/data/projects/' + project_id + '/subjects/' + subject_id + '/experiments?ID=' + exam_no + '/resources/' + resources + '/scans/ALL/files?format=zip'

    # Logging into XNAT/ creating session
    session = requests.Session()    # Stores all the info we need for our session
    session.auth = (xnat_username, xnat_password)
    jsession_id = session.post(jsession_url)

    # Put JSESSION auth ID returned by XNAT rest api inside cookies header
    # Now only the JSESSION ID is available to headers,
    # No XNAT username or password is stored
    session.text = {
        "cookies":
        {
            "JSESSIONID": jsession_id.text
        }
    }


    #................................................
    #...........GET SESSION LIST.....................
    #................................................
    dt = datetime.datetime.now()
    year_month_day = str(dt.year) + str(dt.month) + str(dt.day)
    session_list_csv = bidsonly_path + '/XNAT_metadata/mrsessions_' + year_month_day + '.csv'
    print('starting download')

    if not os.path.exists(os.path.dirname(session_list_csv)):
        try:
            print("Creating directory structure for " + session_list_csv.split('/')[-1])
            os.makedirs(os.path.dirname(session_list_csv))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    with open(session_list_csv, 'wb') as f:
        print("Opening file to write response contents to...")
        with session.get(session_list_url, stream=True) as r:
            print("Checking status...")
            if not r.raise_for_status():
                print("no status returned")
            print("Writing file (this could take some time)...")
            # download in chunks to save buffer memory on doctor
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)
                # print("~~ writing chunks ~~~")
    #................................................
    #...........END GET SESSION LIST.................
    #................................................


    #................................................
    #...........DOWNLOAD SCANS FROM XNAT.............
    #................................................

    # Read mrsession csv and extract labels
    # Scans will ultimately be downloaded by their session label
    with open (session_list_csv, 'r') as f:
        print("Reading and parsing session csv file...")
        lines = f.readlines()
        lines.pop(0)    # Remove 1st line of column labels as they are not exams
        labels = []
        print("Pulled info on " + str(len(lines)) + " sessions.")
        mrsession_ids = []

        for line in lines:
            
            args = job.split()
            arg_no = 0

            label = line.split(',')[-2]
            labels.append(label)
            # mrsession_id = line.split(',')[0]
            # mrsession_ids.append(mrsession_id)

            # Pull accession_no from list of project sessions if exam number
            # matches input args and only download those exams
            print('Scanning list for requested exams...')
            if label in download_queue:
                print('Found exam ' + str(label) + '. Downloading...')

                print("Args for job " + str(active_job_no) + ' of ' + str(total_jobs) + ": " )
                print(*args)
                print("\n")

                bidsonly_exam_path = bidsonly_path + label
            
                mrsession_id = line.split(',')[0]
                mrsession_ids.append(mrsession_id)
                scan_download_url = str(xnat_url + '/data/experiments/' + mrsession_id + '/scans/ALL/resources/' + resources + '/files?format=zip&structure=legacy')
                # scan_download_url = xnat_url + '/data/archive/projects/' + project_id + '/experiments/' + mrsession_id + '/scans/ALL/resources/' + resources + '/files?format=zip&structure=legacy'
                unzipped_path = bidsonly_path + '/' + label
                zipfile = label + '.zip'
                zipfile_path = bidsonly_path + zipfile

                print('Entering scan download stage...')
    # IF EXAM FOLDER EXISTS DO NOT WRITE
    # TODO: Implement checksums to patch missing data seamlessly
                if not os.path.exists(unzipped_path):
                    try:
                        print("Creating directory structure for " + zipfile)
                        os.makedirs(os.path.dirname(zipfile_path))
                    except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            raise
                else:
                    print(unzipped_path + "\nDirectory exists for " + exam_no + ". Moving to next exam in working list.")
                    continue
    # WRITE ZIPFILE OF CURRENT SCAN
                with open(zipfile_path, 'wb') as f:
                    print("Opening file to write response contents to...")
                    with session.get(scan_download_url, stream=True) as r:

                        print("Checking status...")
                        if not r.raise_for_status():
                            print("no status returned")
                        print("Attempting to write file...")
                        chunk_size = 128
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            f.write(chunk)
                            print("~~ writing " + str(chunk_size) + "mb chunks ~~~")
                    # Put close session command here
                print("attempting to unzip " + zipfile_path)
                with ZipFile(zipfile_path, 'r') as zipObj:
                    zipObj.extractall(bidsonly_path)
                    print("should have unzipped")
    #................................................
    #..............END XNAT DOWNLOAD.................
    #................................................

if __name__ == '__main__':
    download_niftis()