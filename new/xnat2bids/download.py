import os

from setup import uid, gid
from fix_perms import fix_perms

# Function to download files from xnat
def download(session, url, path, chunk_size):
   
    with open(path, 'wb') as f:
        print("Opening file to write: " + path)
        with session.get(url, stream=True) as r:
            print("Writing file (this could take some time depending on doctor i/o load)...")
            # download in chunks to save buffer memory on doctor
            chunk_count=0
            for chunk in r.iter_content(chunk_size):
                chunk_count+=1
                chunk_mb = chunk_size/1000000
                # print('Chunk #' + str(chunk_count) + ': writing ' + str(chunk_mb) + ' mb')
                f.write(chunk)
                file_size = chunk_size*chunk_count/1000000
                # print('File size: ' + str(file_size) + ' mb')
            print('Finished downloading ' + path + '. Fixing permissions.')
            fix_perms(path=path, uid=uid, gid=gid)
        