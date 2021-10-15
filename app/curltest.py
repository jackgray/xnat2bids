import subprocess
xnat_url = "https://xnat.nyspi.org"
jsession_url = str(xnat_url + "/data/JSESSION")
print(jsession_url)
jsession_token = subprocess.run(["curl", jsession_url, "-X", "POST"], capture_output=True)
print(jsession_token)

# local url="$host/data/JSESSION"
#     if [[ -n $jses ]]; then
#         curl --cookie JSESSIONID=$jses "$url" -X DELETE >/dev/null 2>&1
#     fi
#     jses=`curl -u $uname:$pass "$url" -X POST 2>/dev/null`