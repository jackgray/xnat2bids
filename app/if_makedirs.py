from os.path import isdir, dirname, exists
from os import makedirs, chmod, chown
from fix_perms import fix_perms
from setup import uid, gid

def if_makedirs(path):
    if not exists(dirname(path)):
        print("Creating directory: ", dirname(path))
        makedirs(dirname(path))
        fix_perms(dirname(path))