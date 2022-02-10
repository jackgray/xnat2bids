from getpass import getpass
from os import path

import encrypt
import make_alias
from constants import encrypted_token_path, username

def make_user_token():
    encrypt.make_token(encrypted_file_path=encrypted_token_path, username=username, password=getpass("\n\nPlease enter your XNAT password: "))

    make_alias.make_alias()
    # try:
    #     make_token(encrypted_file_path=constants.encrypted_token_path, username=getpass("\n\nPlease enter your XNAT username: "), password=getpass("\n\nPlease enter your XNAT password: "))
    # except:
    #     print("I was unable to generate your token :( ")
    #     print("Try running the script again.")

# make_user_token()