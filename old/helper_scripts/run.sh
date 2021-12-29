#!/bin/bash
indir=/MRI_DATA/nyspi/patensasc/derivatives/radiologicsbids
outdir=/home/grayjoh/xnat2bids/out
freesurferlicense=/MRI_DATA/freesurferlicense.txt
log=./log.txt

# usage()
# {
#   echo "usage: $0 [-i xnat_input_base_directory -o output_directory] | [-h] "
# }
# # ############################## #
# # ########### MAIN ############# #
# # ############################## #
# if [ "$1" == "" ]; then
#   usage
#   exit 1
# fi

# if [[ $# -eq 1 ]]; then
#   usage
#   exit
# fi

# if [[ $# -lt 0 ]]; then
#   usage
#   exit 1
# fi
# while [ "$1" != "" ]; do
#     case $1 in
#         -i )           shift
#                        indir=$1
#                        ;;
#         -o )           shift
#                        outdir=$1
#                        ;;
#         * )            usage
#                        exit 1
#     esac
#     shift
# done
# #
# Could error check for volumes being available and such
echo Launching xnat2bids pipelines on $indir 
echo Output will be written to $outdir 

docker run \
    --user=root \
    --name xnat2bids_test-container \
    --mount type=bind,source=$freesurferlicense,target=/opt/freesurfer/license.txt \
    --mount type=bind,source="$indir",target=/input \
    --mount type=bind,source="$outdir",target=/output \
    xnat2bids_test-image \
    python3 /src/xnat2bids.py $indir $outdir \