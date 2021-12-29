from getpass import getpass
from os import path

from encrypt import make_token
from setup import encrypted_token_path

def make_user_token():
    make_token(encrypted_file_path=encrypted_token_path, username=getpass("\n\nPlease enter your XNAT username: "), password=getpass("\n\nPlease enter your XNAT password: "))

    # try:
    #     make_token(encrypted_file_path=setup.encrypted_token_path, username=getpass("\n\nPlease enter your XNAT username: "), password=getpass("\n\nPlease enter your XNAT password: "))
    # except:
    #     print("I was unable to generate your token :( ")
    #     print("Try running the script again.")

# make_user_token()