from os import chown, chmod, walk
from os.path import join
import stat

from setup import uid, gid

def fix_perms(path):
    
    for dirpath, dirnames, filenames in walk(path, topdown=True):  
        # print("\n   Changing permissions on ", dirpath, " for uid: ", uid, " and gid: ", gid) 
        chown(dirpath, uid, gid)
        chmod(dirpath, 0o770)

        for filename in filenames:
            # print("\n************* Fixing permissions on ", filename, " *********************")
            fix = join(dirpath, filename)
            # print("\n   Fixing perms for ", fix)
            chown(fix, uid, gid)
            chmod(fix, 0o770)
                