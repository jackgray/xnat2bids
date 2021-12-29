import os, stat
import errno
import requests
import json

from setup import encrypted_alias_path, jsession_url
from decrypt import decrypt
from make_alias import make_alias

def login(encrypted_alias_path):
    print("\n\n************************** login **********************\n")
    def get_jsession():
# Import and decrypt stored alias token, split into alias and secret
        alias, secret = "", ""
        if os.path.exists(encrypted_alias_path):
            print("\nLocated alias file. Decrypting...")
            (alias, secret) = decrypt(encrypted_alias_path) 
            print("Decrypted alias token.") 
        else:
            print("Could not find an alias file. Asking XNAT for a new one.")
            make_alias()
            print('Made new alias token. Re-attempting decryption.')
            (alias, secret) = decrypt(encrypted_alias_path)
            print("Decrypted alias token.")
        #.....................................................
        #   2nd session: use the alias tokens to request JSESSION token
        #.....................................................
        session = requests.Session()    # Stores all the info we need for our session
        if alias: 
            session.auth = (alias, secret)
            print("\nRequesting JSESSION token from XNAT.")
            jsession_id = session.post(jsession_url)
            if jsession_id.status_code == 200:
                print("XNAT responded with JSESSION token.")

                # Put JSESSION auth ID returned by XNAT rest api inside cookies header
                # Now only the JSESSION ID is available to headers,
                session.text = {
                    "cookies":
                    {
                        "JSESSIONID": jsession_id.text
                    }
                }
            else:
                print("Error occured getting JSESSION token. Requesting new alias token.")
                make_alias()
                get_jsession()
        
        return session
    # session=get_jsession()
    # return session
    return get_jsession()