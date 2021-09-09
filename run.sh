#!/bin/bash
INPUT_DIR=/MRI_DATA/nyspi/test
OUTPUT_DIR=/home/grayjoh/xnat2bids/out

docker run -it \
    --name xnat2bids_test-container \
    --mount type=bind,source="$INPUT_DIR",target=/opt \
    --mount type=bind,source="$OUTPUT_DIR",target=/out \
    xnat2bids_test-image \
    python3 /opt/xnat2bids.py $INPUT_DIR $OUTPUT_DIR
    
    