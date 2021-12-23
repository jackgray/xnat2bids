from os import path, makedirs

def if_makedirs(path):
    if not path.isdir(path):
        makedirs(path)