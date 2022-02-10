
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes

from constants import public_key_path

def make_token(encrypted_file_path, username, password):
    # Create padding function so that password is multiple of 8 no matter what
    def pad(text):
        while len(text) % 8 != 0:
            text += " "
        return text
    delimiter = " ".encode("utf-8")

    # Check for private/public keys -- make them if they can't be found
    # if not os.path.isfile(public_key_path) or not os.path.isfile(private_key_path):
    #     print("Couldn't locate one or both RSA private/public keys. Making new ones. WARNING: this will require all users to re-authenticate.")
    #     make_keys()
    # OPEN FILE
    with open(encrypted_file_path, "wb") as encrypted_file:
        print("\n.....encrypting.....")
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

    from constants import username
    print("\nEncrypted auth info for user " + username + \
        ' and stored it in ' + encrypted_file_path + ' (container path) \n')

