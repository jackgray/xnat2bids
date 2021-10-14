from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512, SHA384, SHA256, SHA, MD5
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
import subprocess
import getpass
hash = "SHA-256"

secure_send_text = 'password'
secure_send_text.encode("utf-8")
print(secure_send_text)

# Public rsa key xnat2bids.pub must be placed in 
# <project ID>/.tokens
pub_key_path = '/Users/j/MRI_DATA/nyspi/patensasc/.tokens/xnat2bids.pub'
public_key = RSA.importKey(open(pub_key_path).read())
print("\npublic_key:\n" + public_key + "\n")
session_key = get_random_bytes(16)
print("\nsession_key: \n" + session_key + "\n")

# Encrypt a new session key with public RSA key
cipher_rsa = PKCS1_OAEP.new(public_key)
print("\ncipher_rsa: \n" + cipher_rsa + "\n")
encrypted_session_key = cipher_rsa.encrypt(session_key)
print("\nencrypted_session_key: \n" + encrypted_session_key + "\n")

# Encrypt password with AES session key
cipher_aes = AES.new(session_key, AES.MODE_EAX)
print("\ncipher_aes: \n" + cipher_aes + "\n")
ciphertext, tag = cipher_aes.encrypt_and_digest(secure_send_text)
print("\nciphertext : \n" + ciphertext + "\n")


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