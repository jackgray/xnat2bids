from zipfile import ZipFile
from os import remove, path

from setup import zipfile_path, bidsonly_path, uid, gid
from fix_perms import fix_perms

def unzip(zipfile_path):
    dst = path.dirname(zipfile_path)
    # Collect filenames for contents of zipfile
    with ZipFile(zipfile_path, 'r') as zip:
        zipped_files = zip.namelist()      
    # Use thoes filenames in a loop to extract them file by file
    for file in zipped_files:
        # src_path = setup.bidsonly_path + '/' + file
        print("Unzipping " + file + '...')
        try:
            with ZipFile(zipfile_path, 'r') as zip:
                zip.extract(file, dst)
        except:
            print("Error extracting " + file)

        fix_perms(path=dst, uid=uid, gid=gid)
    print('Exam archive successfully unzipped. Removing...')
    try:
        remove(zipfile_path)
        print("Deleted " + zipfile_path)
    except:
        print("Unable to delete " + zipfile_path)

    


        