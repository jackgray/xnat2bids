#!/bin/bash

# USE: bash build.sh <path-to-file-to-add-to-image-during-build> <2nd-file>

# First generate conda lock file for environment config to add to build
# nevermind- conda not installed on doctor
docker buildx build \
--platform linux/arm64 \
--push \
-t jackgray/bids_json_generator:arm64latest \
../json_generator