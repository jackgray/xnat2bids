from Crypto.PublicKey import RSA
from constants import private_key_path, public_key_path
# from make_user_tkn import make_user_token

def make_keys():
    # if input("WARNING: continuing will require all users to re-create user tokens (can be done by running this script). Would you like to continue? (y): ") == 'y':
    # Create rsa key
    # password = getpass("Container password: ")  # Use this for extra layer
    print("WARNING: MAKING NEW AUTH KEYS. THIS WILL IMPACT ALL USERS.")
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

    print("Made new public/private keys. Taking you to create a new login token.")

    # make_user_token()
# else:
    # print("Cancelling creation of new public/private keys. Exiting program \n")
    # exit