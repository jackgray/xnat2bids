
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

# TODO: implement additional layer by creating rsa tokens with a passphrase

# project_id = 'patensasc'
# project_path = '/Users/j/MRI_DATA/nyspi/patensasc'

# Open encrypted password token file
# Token file path should be mounted to container
#   --> remove project_path var from token file path

def decrypt(project_path, project_id):

    encrypted_file_path = project_path + '/.tokens/xnat2bids_' + project_id + '_login.bin'

    print("\nencrypted_file_path : \n")
    print(encrypted_file_path)

    with open(encrypted_file_path, "rb") as encrypted_file:
            
        print("\nencrypted_file : \n")
        print(encrypted_file)

        private_key_path = project_path + '/.tokens/xnat2bids_private.pem'
        private_key = RSA.import_key(open(private_key_path).read())

        print("\nprivate_key: \n")
        print(private_key)

        encrypted_session_key, nonce, tag, ciphertext = \
            [ encrypted_file.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

        # Decrypt session key with private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(encrypted_session_key)

        # Decrypt the password with AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        password = cipher_aes.decrypt_and_verify(ciphertext, tag)

    if len(password) > 0:
        # Remove this for production!
        print("Decoded message: " + password.decode("utf-8"))


if __name__ == '__main__':
    decrypt()