from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

import setup

def decrypt(encrypted_file_path):
    #............................................................
    #         DECRYPT
    #............................................................
    with open(encrypted_file_path, "rb") as encrypted_file:
        # Where to find the private key  
        # Import and format the private key
        private_key = RSA.import_key(open(setup.private_key_path).read())
        encrypted_session_key, nonce, tag, ciphertext = \
            [ encrypted_file.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]
        # Decrypt session key with private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(encrypted_session_key)
        # Decrypt the password with AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        username_password = cipher_aes.decrypt_and_verify(ciphertext, tag)
    # Check if auth token was successfully decrypted and
    # split username and password into separate variables
    if len(username_password) > 0:
        username_password = str(username_password\
            .decode("utf-8"))\
                .strip()\
                    .split()
        username = username_password[0].strip()
        password = username_password[1].strip()
    else:
        print("Could not retrieve xnat login password. There was likely a problem retrieving or decrypting your login token.")

    return username, password