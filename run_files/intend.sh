#!/bin/bash
#
# Run BIDS pipelines based on xnat data
#

# ############################## #
# ########### MAIN ############# #
# ############################## #

projid=$1
subjid=$2
exam=$3
path=$4

echo -en "======================== RUNNING mkvalid on: ${projid}-${subjid} ============================\n\n"

export tbase="/usr/local/sbin"
fulldir="/data/${projid}"

#
# Check that BIDS structure was created as expected prior to doing anything further
#
if [ ! -f ${fulldir}/rawdata/dataset_description.json ]; then
  echo "Prerequisite BIDS setup seems incomplete on $fulldir. Quitting"
  exit 1
fi
if [ ! -d ${fulldir}/rawdata/sub-${subjid} ]; then 
  echo "$subjid does not exist in $fulldir under rawdata. Quitting."
  exit 1
fi
if [ ! -d ${fulldir}/derivatives ]; then 
  echo "Derivatives folder does not exist in $fulldir. Odd so quiting."
  exit 1
fi
#
# Assign IntendedFor to FMAP files with fpe or rpe names based on aquisition time
#
${tbase}/intendedFor.py ${fulldir}/rawdata/sub-${subjid} ${exam} 2&>> ${fulldir}/derivatives/mkvalidbids.out
cd ${fulldir}/rawdata/sub-${subjid}/ses-${exam}/fmap
#
newstuff=(*_new)
if [ -e "${newstuff[0]}" ]; then 
  for newfile in *_new;
  do
    oldfile=${newfile%"_new"}
    mv $oldfile ${fulldir}/derivatives
    mv $newfile $oldfile
  done  
else
  echo "No IntendedFor changes applied."
fi
#
# Assign TaskName to FUNC files using SeriesDescription
#
${tbase}/taskName.py ${fulldir}/rawdata/sub-${subjid}/ses-${exam}  2&>> ${fulldir}/derivatives/mkvalidbids.out
cd ../func
newstuff=(*_new)
if [ -e "${newstuff[0]}" ]; then 
  for newfile in *_new;
  do
    oldfile=${newfile%"_new"}
    mv $oldfile ${fulldir}/derivatives
    mv $newfile $oldfile
  done  
else
  echo "No TaskName changes applied."
fi
#
echo "===================================================="
echo -en "======================== COMPLETED mkvalid ================================\n\n"
