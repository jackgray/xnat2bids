
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import os

from setup import public_key_path, private_key_path
from make_kys import make_keys



def make_token(encrypted_file_path, username, password):

    # Create padding function so that password is multiple of 8 no matter what
    def pad(text):
        while len(text) % 8 != 0:
            text += " "
        return text

    delimiter = " ".encode("utf-8")

    # Check for private/public keys -- make them if they can't be found
    if not os.path.isfile(public_key_path) or os.path.isfile(private_key_path):
        make_keys()
    # OPEN FILE
    # This is unique to each project and should be stored in /MRI_DATA/.xnatauth
    with open(encrypted_file_path, "wb") as encrypted_file:
        print("\n.....encrypting.....")
        # Public rsa key xnat2bids_public.pem should be stored in secure location
        # accessible only by this script
        public_key = RSA.importKey(open(public_key_path).read())

        session_key = get_random_bytes(16)

        # Encrypt a new session key with public RSA key
        cipher_rsa = PKCS1_OAEP.new(public_key)

        encrypted_session_key = encrypted_file.write(cipher_rsa.encrypt(session_key))

        # Encrypt password with AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)

        # on the decrypt side, we will separate the token with the space (' ') character
        # add one just in case
        ciphertext, tag = cipher_aes.encrypt_and_digest(pad(username).encode("utf-8") + delimiter + pad(password).encode("utf-8"))

        encrypted_file.write(cipher_aes.nonce)
        encrypted_file.write(tag)
        encrypted_file.write(ciphertext)

    print("\n\n\n\nEncrypted auth info for user " + username + \
        ' and stored it in ' + encrypted_file_path + ' (container path) \n')

