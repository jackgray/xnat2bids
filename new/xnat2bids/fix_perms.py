from os import chown, chmod
import stat

def fix_perms(path, uid, gid):   
    chown(path, uid, gid)
    chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IRWXG | stat.S_IRWXU | stat.S_IRWXO)
