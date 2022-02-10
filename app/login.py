import os, stat
import requests

from constants import jsession_url
import decrypt
import make_alias

def xnat_login(encrypted_alias_path):
    print("\n\n************************** logging into XNAT **********************\n")
    def get_jsession():     # Import and decrypt stored alias token, split into alias and secret
        alias, secret = "", ""
        if os.path.exists(encrypted_alias_path):
            print("\nLocated alias file. Decrypting...")
            (alias, secret) = decrypt.decrypt(encrypted_alias_path) 
            print(" Decrypted alias token.") 
        else:
            print("Could not find an alias file. Asking XNAT for a new one.")
            make_alias.make_alias()
            print(' Made new alias token. Re-attempting decryption.')
            (alias, secret) = decrypt.decrypt(encrypted_alias_path)
            print(" Decrypted alias token.")

        xnat_session = requests.Session()    # Stores all the info we need for our session
        if alias:  # Don't bother requesting if alias wasn't decrypted
            xnat_session.auth = (alias, secret)
            print("\nRequesting JSESSION token from XNAT.")
            jsession_id = xnat_session.post(jsession_url)
            if jsession_id.status_code == 200:
                print(" XNAT responded with JSESSION token. Ready to download! \n")
                # Put JSESSION auth ID returned by XNAT rest api inside cookies header. Now only the JSESSION ID is available to headers,
                xnat_session.text = {
                    "cookies":
                    {
                        "JSESSIONID": jsession_id.text
                    }
                }
            else:
                print("Error occured getting JSESSION token. Requesting new alias token.")
                make_alias.make_alias()
                get_jsession()
        else:
            print("There was a problem decrypting your alias token file. Requesting new alias token from XNAT...")
            make_alias.make_alias()
        return xnat_session
    return get_jsession()

# def sdc_login():

#     with sshtunnel.SSHTunnelForwarder(
#         (_host, _ssh_port),
#         ssh_username=_username,
#         ssh_password=_password,
#         remote_bind_address=(_remote_bind_address, _remote_mysql_port),
#         local_bind_address=(_local_bind_address, _local_mysql_port)
#     ) as tunnel:
#     connection =

#     sdc_session = requests.Session()