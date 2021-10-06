#!/bin/bash
#
#This script will perform below tasks based on the arguments:
#1) Sync data from xnat based on input.
#2) Create data structure and run dcm2bids.
#3) Convert/split multivolume topup files.
#4) Apply intendedFor and taskName.
#5) Run bids-validator on the data.
#
#
###### BEGIN ########
#Usage message to display
usage()
{
  echo -en "\nSYNTAX ERROR\n"
  echo -e "usage: $0 [ -d directory -p project_id -a arguments ]\n"
  echo -e "Where directory is before the projects\n"
  echo -en "[arguments] can be:\n"

#
if [ "$1" == "" ]; then
  usage
  exit 1
fi

if [[ $# -eq 1 ]]; then
  usage
  exit
fi

if [[ $# -lt 3 ]]; then
  usage
  exit 1
fi

while [ "$1" != "" ]; do
    case $1 in
        -d )           shift
                       dept=$1
                       ;;
        -p )           shift
                       projid=$1
                       ;;
        -a)            shift
                       arg=$1
                       ;;
        * )            usage
                       exit 1
    esac
    shift
done
#

#
### Assuming below directory structure ####
### Example:
### dept=directory
### List path: /baseDIR/dept/projectID/scripts/projectID_working.lst
### Raw data path: /baseDIR/dept/projectID/rawdata/
### Subject path: /baseDIR/dept/projectID/rawdata/sub-subjectID/
### d2b-template_projectID.json path: /baseDIR/dept/projectID/d2b-template_projectID.json
### dataset_description.json path: /fileloc/dataset_description.json
### participants.tsv path: /fileloc/participants.tsv
###
### To run from a different host or different path, 3 variables need to be changed
### "basedir", "dept" and "fileloc"
### In this script, basedir=/MRI_DATA
###                 dept=nyspi
###            and, fileloc=/usr/local/pipelines
#
#
user=`id -un`
homedir=`echo ~`
image="nyspishared/xnat2bids:latest"
basedir="/MRI_DATA"
#
#Ask for xnat username and password only if running sync 
if [[ "$arg" = *sync* ]]; then
# Check if netrc file is not present
        if ! [[ $(ls -d ${basedir}/.xnatrc/.netrc_${user} 2>/dev/null) ]] ; then
                ## If netrc file is not present, Ask for xnat username and password
                read -p "Enter XNAT username: " xnatname
                read -s -p "Password: " xnatpass
                (cat <<<"machine xnat.nyspi.org login ${xnatname} password ${xnatpass}") > ${basedir}/.xnatrc/.netrc_${user} && chown ${user} ${basedir}/.xnatrc/.netrc_${user} && chmod 600 ${basedir}/.xnatrc/.netrc_${user}
                echo
        fi
fi
#
prodir=${basedir}/${dept}/${projid}
listpath=${prodir}/scripts/${projid}_working.lst
bidsonlypath=${prodir}/derivatives/bidsonly
tmpdir=${prodir}/${projid}/tmp
xnatdir="/XNATdata"
#
#default description and tsv file location for convertdcm:
fileloc="/usr/local/pipelines"
#
#If project list file is not present, then exit
if [ ! -f ${listpath} ]; then
  echo -en "\nERROR:\n${projid}_working.lst is not present under ${listpath}/.\nCannot proceed without this file.\n\n"
  exit
fi
#
#If json template of the project is not present, then exit
if [ ! -f ${prodir}/d2b-template_${projid}.json ]; then
  echo -en "\nERROR:\nd2b-template_${projid}.json file is not present under ${prodir}/${projid}/.\nCannot proceed without this file.\n\n"
  exit
fi
#If the subjects are more than 10, then exit
#if [ $(grep -c . ${listpath}/${projid}_working.lst) -gt 10 ]; then
#  echo -en "\nERROR:\nOnly 10 subjects allowed at once.\n\n"
#  exit
#fi
#
#
#Optional - Pending - to check for below files if they exist or not, and exit if not:
# pre-bidsprep-perms.sh, post-bidsprep-perms.sh, dataset_description.json, participants.tsv,
# d2b-template_${projid}.json, /bidsq.sh
#
#Make a temp directory
mkdir -p ${tmpdir}
# && chmod 770 ${tmpdir}
#Copy monitoring script to temp directory
cp ${fileloc}/bidsqmonitor.sh ${tmpdir}/bidsqmonitor_${projid}.sh
#Delete any previous cronjob for this specific monitoring
crontab -l | sed "/bidsqmonitor_${projid}/d" | crontab -

#Empty/Create a file inside temp directory that has a list service names used for monitoring
cat /dev/null > ${tmpdir}/${projid}_working.service.lst

#Backup the original working list file
if ! [[ $(ls -d ${listpath}.orig 2>/dev/null) ]] ; then cp ${listpath} ${listpath}.orig; fi

#Create a temp file of the original working list inside temp directory
if ! [[ $(ls -d ${tmpdir}/${projid}_working.lst.tmp 2>/dev/null) ]] ; then cp ${listpath} ${tmpdir}/${projid}_working.lst.tmp; fi

#If tmp file is empty, then delete the whole temp directory and exit
if [ $(cat ${tmpdir}/${projid}_working.lst.tmp | wc -l) == 0 ]; then
        mv ${listpath}.orig ${listpath} \
        && rm -rf ${tmpdir} 2>/dev/null
        exit
fi
#
if [[ "$arg" = *sync* ]]; then
        netrcmount="--mount type=bind,source=${basedir}/.xnatrc/.netrc_${user},destination=/.nrc/.netrc"
else
        netrcmount=""
fi

#Get the gid of the project group
progroup=$(cat /etc/group | grep ${projid} | cut -d ":" -f3)


#Set job limit to 5
#Copy first 5 lines of the temp working list file to the original working list file
awk 'NR >= 1 && NR <= 5' ${tmpdir}/${projid}_working.lst.tmp > ${listpath}/${projid}_working.lst
sleep 1
#Delete the first 5 lines of the temp working list file
sed -i '1,5d' ${tmpdir}/${projid}_working.lst.tmp
#
#Read the original working list file that has 5 lines and launch the jobs
#
sleep 2
grep . ${listpath} | while read -r line
do
subjid=$(echo $line | awk '{print $1}')

# Keeping identical structures allows this to be run 
# outside of container more easily
bidsonlypath_doctor="/Users/j/${projdir}/derivatives/bidsonly"
bidsonlypath_container="${prodir}/derivatives/bidsonly"
rawdatapath_doctor="/Users/j/${prodir}/rawdata"
rawdatapath_container="${prodir}/rawdata"

exam=$(echo $line | awk '{print $3}')
accession=$(echo $line | awk '{print $4}')
#log=${prodir}/${projid}/derivatives/sub-bidsprep.log
log=${HOME}/sub-bidsprep.log
name=${dept}_${projid}_${subjid}_${exam}_${user}
echo "Starting service for ${name}" >> ${log}
nohup /usr/bin/docker service create\
    --replicas 1\
    --reserve-cpu 8\
    --reserve-memory 16g\
    --mode replicated\
    --restart-condition none\
    --name=${name}\
    --mount type=bind,\
    source=${rawdatapath_doctor},\
    destination=${rawdatapath_container}\
    --mount type=bind,\
    source=${bidsonlypath_doctor},\
    destination=${bidsonlypath_container}\
    --mount type=bind,\
    source=${listdir},\
    destination=${listdir}\
    --mount type=bind,\
    source=${prodir}/.cp_pre-bidsprep-perms.sh,\
    destination=/bin/pre-perms.sh\
    --mount type=bind,\
    source=${prodir}/.cp_post-bidsprep-perms.sh,\
    destination=/bin/post-perms.sh\
    ${netrcmount}\
    ${image}\
    python3 dn_nifti.py ${projid};\
    python3 nifti2bids.py ${projid}
echo ${name} >> ${tmpdir}/${projid}_working.service.lst
done
echo -en "Jobs submitted for project \"${projid}\" with argument \"${arg}\".\nPlease run ${fileloc}/sub-bidsmgmt to manage the jobs.\n"
#
#Monitoring the queue:
#
#Create a cronjob that runs the monitoring script every 5 mins
sleep 5
(crontab -l && echo "*/5 * * * * ${tmpdir}/bidsqmonitor_${projid}.sh ${dept} ${projid} ${arg}") | crontab -
##### END #####
