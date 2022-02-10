from os.path import isdir, dirname, exists
from os import makedirs, chmod, chown, walk
from fix_perms import fix_perms
from constants import uid, gid

def if_makedirs(path):
    if not exists(dirname(path)):
        print("Creating directory: ", dirname(path))
        makedirs(dirname(path))
        fix_perms(dirname(path))

# def if_makedirs(path):
#     directory = dirname(path)
#     print("Dirname: ", directory)
#     for root, dirs, files in walk(directory, topdown=False):
#         for name in files:


# os.makedirs(path, mode=0o770, exist_ok=True)