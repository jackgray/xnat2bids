from os import path

from make_user_tkn import make_user_token
from make_alias import make_alias
from download_exam import download_exam
import setup

# TODO: make separate private/public keyfiles for user vs. alias encryptions

# if not path.isfile(setup.encrypted_token_path):
    # encrypt_user_login()    # prompts for password, encrypts it, then stores it
# if not path.isfile(setup.encrypted_alias_path):
# make_alias()    # retrieves user login token, decrypts it, requests alias key:value pair from XNAT, then encrypts and stores that

download_exam(exam=setup.exam_no)    # uses alias token to get jsession and downloads