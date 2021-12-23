from Crypto.PublicKey import RSA
import setup

# Create rsa key
# password = getpass("Container password: ")  # Use this for extra layer
key = RSA.generate(2048)  # no known cracks of rsa-2048 
private_key = key.exportKey()
private_key_file = open(setup.private_key_path, "wb")
private_key_file.write(private_key)
private_key_file.close()

public_key = key.publickey().exportKey()
public_key_file = open(setup.public_key_path, "wb")
public_key_file.write(public_key)
public_key_file.close()

print(key.publickey().exportKey())
