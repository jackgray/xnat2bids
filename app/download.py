import os

from fix_perms import fix_perms
from if_makedirs import if_makedirs

# Function to download files from xnat
def download(session, url, path, chunk_size):
    if_makedirs(path)
    with open(path, 'wb') as f:
        print("\nOpening file to write: " + path)
        with session.get(url, stream=True) as r:
            print("Writing file (this could take a few minutes--depends on server i/o load)...")
            # download in chunks to save buffer memory on doctor
            chunk_count=0
            for chunk in r.iter_content(chunk_size):
                f.write(chunk)
                chunk_count+=1
                if chunk_count % 325 == 0:
                    print("...writing file...")
                
            print('\nFinished downloading ' + path + '. Fixing permissions.')
            fix_perms(path=path)
        