import pycurl
import shutil
from io import BytesIO

xnat_username = 'grayjoh'
xnat_password = 'taprik-2vacno-naTbag'
xnat_url = 'https://xnat.nyspi.org'
jsession_url = xnat_url + '/data/JSESSION'
project_id = 'patensasc'
subject_id = 'patensasc4018'
exam_no = '1069'
resources = 'BIDS'


session_list_url = 'https://xnat.nyspi.org/data/archive/projects/patensasc/experiments?xsiType=xnat:mrSessionData&format=csv&columns=ID,label,xnat:subjectData/label%22'
bids_resource_url = xnat_url + '/data/projects/' + project_id + '/subjects/' + subject_id + '/experiments?xsiType=xnat:mrSessionData/scans/' + exam_no + '/resources/' + resources + '/files?format=zip'

buffer = BytesIO()
j_session = pycurl.Curl()
j_session.setopt(j_session.URL, jsession_url)
j_session.setopt(j_session.USERPWD, xnat_username + ':' + xnat_password)
j_session.setopt(j_session.TIMEOUT, 10)
j_session.setopt(j_session.FOLLOWLOCATION, 1)
j_session.setopt(j_session.PUT, 1)
j_session.setopt(j_session.WRITEDATA, buffer)

j_session.perform()

# cookies = requests.cookies.RequestsCookieJar()
# cookies.set('JSESSION_ID', jsession_id.text)

# session.text = {
#     "cookies":
#     {
#         "JSESSIONID": jsession_id.text
#     }
# }


# bids = session.get(bids_resource_url)
# print(bids)

# print(jsession_id.text)
# print(session.text)

# session_list = session.get(\
#     session_list_url
#     )


# curl --cookie JSESSIONID=curl -u $uname:$pass xnat_url + '/data/JSESSION' -X POST
