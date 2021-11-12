# Generates two files, "bidsmap.json" and "d2b-map.json"

input arguments:

    - XNAT username
    - XNAT password
    - xnat project name

Script will scrape every sequence name in that project and create a configuration map to be used in dcm2bids

It can be run unlimited times even if a config file already exists--it will be replaced by a new file with the old configs + new

console log will say how many and which sequences were added, and which sequences were not added and why

a number of log files are also generated to gain a sense of how the program behaves and confirm that all desired sequences are mapped

To use:

download generate-bidsmaps.py

run
python3 generate-bidsmaps.y

login to XNAT at command prompt

enter project ID at command prompt

# TODO: set up argument parser

# TODO: containerize

# TODO: auth XNAT with .env variable for universal user
