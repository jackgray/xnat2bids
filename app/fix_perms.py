# from os import chown, chmod, walk
# from os.path import join, dirname, parent
import os
from constants import uid, gid


# Recursively modifies permissions for all subfolders and files contained in "path"
def fix_perms(path):
    # directory = path.split('/').pop(0).join('/') # removes parent folder from path
    # root = '/' + path.split('/')[1]
    skip_paths = ['/bidsonly', '/neuromelanin', '/derivatives', '/scripts']

    for dirpath, dirnames, filenames in os.walk(path, topdown=True):  
        
        if dirpath not in skip_paths:
            os.chown(dirpath, uid, gid)
            os.chmod(dirpath, 0o770)
            print("Modified perms on : ", dirpath)  
        else:
            print("Skipping perms on ", dirpath, " (should = root, ", root, ")")
        for filename in filenames:
            fix = os.path.join(dirpath, filename)
            os.chown(fix, uid, gid)
            os.chmod(fix, 0o770)
            
    print("Adjusted permissions for ", path)
                