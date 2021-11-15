# Generates two files, "bidsmap*<project ID>.json" and "d2b-template*<project ID>.json"

# Expects xnat auth token created by jackgray/xnat_auth image

USAGE:
docker run \
-e project_id=<project ID> \
--mount type=bind,source=<project directory>,destination=bidsconfig \
--mount type=bind,source=<xnat auth token path>,destination=/tokens,readonly=true \
--mount type=bind,source=<private key path>,destination=/xnat/xnat2bids_private.pem,readonly=true \
jackgray/bids_json_generator:amd64latest;

Script will scrape every sequence name in that project from the XNAT web client and create a configuration map to be used in dcm2bids

It can be run unlimited times even if a config file already exists--it will be replaced by a new file with the old configs + new. It will only add more elements--to remove any elements they must be manually deleted.

console log will say how many and which sequences were added, and which sequences were not added and why

a number of log files are also generated to gain a sense of how the program behaves and confirm that all desired sequences are mapped
