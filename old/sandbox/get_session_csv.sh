# curl -u grayjoh:p@sswd45 -o session.csv -X GET https://xnat.nyspi.org/data/experiments/XNATnyspi19_E00509/?xsiType=xnat:mrSessionData&format=csv&columns=ID,label,type

# curl -u grayjoh:p@sswd45 -o session_list.csv -X GET https://xnat.nyspi.org/data/archive/projects/spanint/experiments?xsiType=xnat:mrSessionData&format=csv&columns=ID,label,xnat:subjectData/label

curl -u grayjoh:p@sswd45 -X GET https://xnat.nyspi.org/data/experiments/XNATnyspi19_E00509/scans
