import getpass
import requests
import json

 # TODO: fix this
xnat_username = 'grayjoh'
xnat_password = 'taprik-2vacno-naTbag'

xnat_url = 'https://xnat.nyspi.org'
alias_token_url_user = xnat_url + '/data/services/tokens/issue'
alias_token_url_admin = alias_token_url_user + '/user/' + xnat_username

#.....................................................
#   1st session: request alias tokens (48hr life)
#.....................................................

session = requests.Session()    # Stores all the info we need for our session
session.auth = (xnat_username, xnat_password)
alias_response = session.get(alias_token_url_user)
alias_resp_text = alias_response.text
alias_resp_json = json.loads(alias_resp_text)
alias = alias_resp_json["alias"]
secret = alias_resp_json["secret"]
print("generated single-use alias :" + alias)
print("generated single-use secret :" + secret)