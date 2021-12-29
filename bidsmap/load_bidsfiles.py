 
from setup import bidsmap_path, dcm2bids_path
 
def load_bidsfiles():
 # Read what exists in bidsmap.json
    try:
        with open(bidsmap_path, mode='r') as jsonFile:
            existing_json_bids = json.load(jsonFile)
    except:
        existing_json_bids = []

    # Read what exists in d2b-map.json
    try:
        with open(dcm2bids_path, mode='r') as jsonFile:
            existing_json_d2b = json.load(jsonFile)
    except:
        existing_json_d2b = []

    # Add everything collected to a text file for reference
    raw_list = list(dict.fromkeys(raw_list))

    with open('/logs/raw_list.txt', 'w') as tmp_file:
        tmp_file.write('\n'.join(map(str,raw_list)))

    # Print sequences found on XNAT
    print(str(len(raw_list)) + ' unique sequences found: \n')
    for i in raw_list:
        print(i)
    print('----------------------------------------------------------')

    # Create a list of sequences already in the json file being read
    print('\nThe following sequences already exist in the bidsmap and will be skipped:\n')
   
    # Load bidsmap.json file
    for i in existing_json_bids:
        print(i['series_description'])
        existing_bids.append(i['series_description'])

    with open('/logs/existing_bids.txt', 'w') as tmp_file:
        tmp_file.write('\n'.join(map(str, existing_bids)))

    print('----------------------------------------------------------')

    print('\nThe following sequences already exist in the d2b file and will be skipped:\n')
    # Load d2b json file
    try:
        for i in existing_json_d2b['descriptions']:
            print(i['criteria']['SeriesDescription'])
            existing_d2b.append(i['criteria']['SeriesDescription'])
    except:
        print("empty list. no worries...")
    try:
        with open('logs/existing_d2b.txt', 'w') as tmp_file:
            tmp_file.write('\n'.join(map(str,existing_d2b)))
    except:
        print("Couldn't open logs/existing_d2b.txt. Does it exist?")
    print('----------------------------------------------------------')

    # Scan collected sequences for duplicates and remove them
    sequence_list = list(dict.fromkeys(sequence_list))
    with open('/logs/sequence_list.txt', 'w') as tmp_file:
        tmp_file.write('\n'.join(map(str,sequence_list)))

    # Filter out sequences that already exist in the map
    not_in_map_bids = list(set(sequence_list).difference(existing_bids))
    with open('/logs/not_in_map_bids.txt', 'w') as tmp_file:
        tmp_file.write('\n'.join(map(str,not_in_map_bids)))

    not_in_map_d2b = list(set(sequence_list).difference(existing_d2b))
    with open('/logs/not_in_map_d2b.txt', 'w') as tmp_file:
        tmp_file.write('\n'.join(map(str,not_in_map_d2b)))

    # Function to add generated scan info to a list
    def addSequence_bids():
        with_bids = {'series_description': i, 'bidsname': bidsname}
        generated_bids.append(with_bids)
        just_added_bids.append(i)
    def addSequence_d2b():
        generated_d2b.append(with_d2b)
        just_added_d2b.append(i)

    # Print sequences to be added to bidsmap
    print('\nAttempting to match the following ' + str(len(not_in_map_bids)) + ' sequences not yet in the bidsmap. \n')

    #######################################################
    #      