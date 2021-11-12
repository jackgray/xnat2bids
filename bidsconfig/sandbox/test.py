import json

filename = 'd2b-template_marsonc.json'

with open(filename, mode='r') as jsonFile:
    existing_json = json.load(jsonFile)
for i in existing_json:
    print(existing_json.get('descriptions')[i]['criteria']['SeriesDescription'])