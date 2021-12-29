from Crypto.PublicKey import RSA
from setup import private_key_path, public_key_path

def make_keys():
    # Create rsa key
    # password = getpass("Container password: ")  # Use this for extra layer
    key = RSA.generate(2048)  # no known cracks of rsa-2048 
    private_key = key.exportKey()
    private_key_file = open(private_key_path, "wb")
    private_key_file.write(private_key)
    private_key_file.close()

    public_key = key.publickey().exportKey()
    public_key_file = open(public_key_path, "wb")
    public_key_file.write(public_key)
    public_key_file.close()

    print(key.publickey().exportKey())
