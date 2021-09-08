#!/bin/bash
INPUT_DIR=/MRI_DATA/nyspi/test
OUTPUT_DIR=/home/grayjoh/xnat2bids

docker run -it \
    --name xnat2bids_test-container \
    --mount type=bind,source="$INPUT_DIR",target=/xnat2bids \
    --mount type=bind,source="$OUTPUT_DIR",target=/xnatbids \
    xnat2bids_test-image \
    python3 /xnat2bids/xnat2bids.py
    