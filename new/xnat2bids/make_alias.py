from os import path, makedirs
import requests
from json import loads

from setup import encrypted_token_path, encrypted_alias_path, alias_token_url
from decrypt import decrypt
from encrypt import make_token
from make_user_tkn import make_user_token

# First, open encrypted xnat token, decrypt it,
# then retrieve alias token from XNAT API,
# then encrypt and store that alias token

#............................................................
#   AUTHENTICATION: alias k:v tokens, then jsession token
#............................................................
# TODO: if login error, go back and run xnat-auth

def make_alias():
    (xnat_username, xnat_password) = [None, None]
    # Decrypt user token, generate new one if there's an error
    if path.exists(encrypted_token_path):
        print("Located token file")
        try:
            (xnat_username, xnat_password) = decrypt(encrypted_token_path)
            print(xnat_username+xnat_password)
        except:
            print("Failed to decrypt XNAT token for user " + xnat_username)
            print("That's okay, we can make a new one together :) ")
            make_user_token()
    else:
        make_user_token()
        (xnat_username, xnat_password) = decrypt(encrypted_token_path)

    # Inititalize requests' session object
    session = requests.Session()    # Stores all the info we need for our session
    if xnat_username:
        session.auth = (xnat_username, xnat_password)
        try:
            alias_response = session.get(alias_token_url) # Gets entire response header object
            alias_response.raise_for_status()
            alias_resp_text = alias_response.text  # Isolate text response 
            alias_resp_json = loads(alias_resp_text)  # Convert into json format
            alias = alias_resp_json["alias"]  # Now that we have key:value pairs it's easy to extract what we want
            secret = alias_resp_json["secret"]
            print("\nGenerated single-use alias.")
            print("Generated single-use secret. Combining them into encrypted token file.")
            
            # makedirs(path=encrypted_alias_path, exist_ok=True)
            print("\nalias: " + alias)
            print("\nsecret: " + secret)
            make_token(encrypted_file_path=encrypted_alias_path, username=alias, password=secret)
            print("Stored encrypted alias token at " + encrypted_alias_path)
            print("File needs to be decrypted before logging in, and will expire in 2 days.")
        except:
            print("Couldn't get alias token. There could be a problem with your xnat token, so let's go ahead and renew that.")
            make_user_token()
            make_alias()    # Re-attempt alias request
        