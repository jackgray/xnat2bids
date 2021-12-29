from zipfile import ZipFile
from os import remove, path

from fix_perms import fix_perms

def unzip(zipfile_path):
    dst = path.dirname(zipfile_path)
    # Collect filenames for contents of zipfile
    with ZipFile(zipfile_path, 'r') as zip:
        zipped_files = zip.namelist()      
    # Use thoes filenames in a loop to extract them file by file
    for file in zipped_files:
        # src_path = setup.bidsonly_path + '/' + file
        print("\n   Unzipping " + file + '...')
        try:
            with ZipFile(zipfile_path, 'r') as zip:
                zip.extract(file, dst)
        except:
            print("\n!!! Error extracting " + file + ". I'll try to continue with the rest.")
        # TODO: recursively fix perms   
        fix_perms(path=dst)
    print('\nArchive successfully unzipped. Removing...')
    try:
        remove(zipfile_path)
        print("Deleted " + zipfile_path)
    except:
        print("Unable to delete " + zipfile_path)

    


        