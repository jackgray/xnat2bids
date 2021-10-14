from hashlib import md5
import warnings
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import getpass
import os
import time

# TODO: store public key in central location.
# - discuss permissions 

project_id = 'patensasc'
project_path = '/Users/j/MRI_DATA/nyspi/' + project_id

token_folder = project_path + '/.tokens'
private_key_path = token_folder + '/xnat2bids_private.pem'
public_key_path = token_folder + '/xnat2bids_public.pem'
encrypted_file_path = token_folder + '/xnat2bids_' + project_id + '_login.bin'

if not os.path.isfile(public_key_path):
    print("I can't find the public rsa token for xnat2bids container.")
    time.sleep(1.5)
    print("Check if xnat2bids_public.pem is in your /.tokens folder or contact a member of the MRI Compute team to get set up.")
    time.sleep(1)
    # PROMPT USER 
    exit()

if not os.path.isfile(encrypted_file_path):
    print("\nHi! Looks like you haven't created a login token or it has expired. ")
    time.sleep(1.5)
    print("No worries! We'll just make a new one :)")
    time.sleep(1)

    # Create padding function so that password is multiple of 8 no matter what
    def pad(text):
        while len(text) % 8 != 0:
            text += ' '
        return text

    # OPEN FILE
    # This is unique to each project and should be stored in .../<project ID>/.tokens (hidden)
    with open(encrypted_file_path, "wb") as encrypted_file:
        print("\nWe'll make it with these objects: ")
        # Public rsa key xnat2bids_public.pem should be stored in secure location
        # accessible only by this script
        public_key = RSA.importKey(open(public_key_path).read())

        print("\npublic_key:")
        print(public_key)

        session_key = get_random_bytes(16)

        print("\nsession_key: ")
        print(session_key)

        # Encrypt a new session key with public RSA key
        cipher_rsa = PKCS1_OAEP.new(public_key)

        print("\ncipher_rsa: ")
        print(cipher_rsa)

        encrypted_session_key = encrypted_file.write(cipher_rsa.encrypt(session_key))

        print("\nencrypted_session_key: ")
        print(encrypted_session_key)

        # Encrypt password with AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)

        print("\ncipher_aes: ")
        print(cipher_aes)

        ciphertext, tag = cipher_aes.encrypt_and_digest(pad(getpass.getpass(\
        "\n\nPlease enter your XNAT login password: "))\
            .encode("utf-8"))

        print("\nciphertext : ")
        print(ciphertext)
        print("\nThis key is unique to each project and should be stored in .../<project ID>/.tokens (hidden)")
        print("Make sure the folder is mounted to the xnat2bids container")

        encrypted_file.write(cipher_aes.nonce)
        encrypted_file.write(tag)
        encrypted_file.write(ciphertext)
    print("\n\n...........................\n\nEncrypted XNAT password for " + project_id + \
        ' and stored it in ' + encrypted_file_path + '\n')


    # replicas = '1'
    # cpus = '2'
    # reserve_memory = '2gb'
    # mode = 'replicated'
    # restart_condition = 'none'
    # service_name = 'xnat2bids'
    # image_name = 'xnat2bids:latest'

    # subprocess.call([\
    # 'docker', 'service', 'create',\
    #     '--replicas', replicas,\
    #     '--reserve-cpu', cpus,\
    #     '--reserve-memory', reserve_memory,\
    #     '--mode', mode,\
    #     '--restart-condition', restart_condition,\
    #     '--name', service_name,\
    #     '--mount', 'type=bind',\
    #     "'source=' + rawdatapath_doctor",\
    #     "'destination=' + rawdatapath_container",\
    #     '--mount', 'type=bind',\
    #     "'source=' + bidsonlypath_doctor",\
    #     "'destination=' + bidsonlypath_container"\
    #     '--mount', 'type=bind',\
    #     "'source=' + workinglistpath_doctor",\
    #     "'destination=' + workinglistpath_container",\
    #     image_name,\
    #     'python3', 'xnat2bids.py', project_id, ciphertext

    # ])


    # # Create rsa key
    # # password = getpass("XNAT Password: ")
    # key = RSA.generate(2048)
    # private_key = key.export_key()
    # private_key_file = open(private_token_path, "wb")
    # private_key_file.write(private_key)
    # private_key_file.close()

    # public_key = key.publickey().export_key()
    # public_key_file = open(public_token_path, "wb")
    # public_key_file.write(public_key)
    # public_key_file.close()

    # print(key.publickey().export_key())