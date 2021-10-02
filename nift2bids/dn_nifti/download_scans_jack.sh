#!/bin/bash

##########################################################################################
#   This file should be the same as original without if statement to catch
#   resource type (-f format) conditions. Now for option -f, anything can be entered.
#   I.e., BIDS,NIFTI is a valid input -- it will fail if spaces are added between commas.
##########################################################################################

usage()
{
cat << EOF
This script downloads scans from XNAT.
USAGE: 
$0 [OPTIONS] [-d output directory] [-o XNAT host URL] [-i projecct ID] 
OPTIONS:
-x    overwrite directories if they exist already (default is to skip the session if a directory by that name already exists)
[-s session labels comma separated] 
[-t typename]       Only download scans of this type (must match the "type" field in XNAT). Can enter a space-separeted list, be sure to quote it (e.g., "MPRAGE REST")
[-f format]         Only download scans in this format (default is to download everything). Choose from DICOM, NIFTI, ANALYZE  
[-u username]       If you don't enter username and password as arguments to the script, you will be prompted to enter them interactively.
[-p password]       If you don't enter username and password as arguments to the script, you will be prompted to enter them interactively.
NOTE:
If you don't enter username and password as arguments to the script, you will be prompted to enter them interactively.
To see this message, enter $0 -h
EOF
}

overwrite=0
scantypes=ALL
while getopts d:u:p:i:s:t:f:o:xh opt
do
    case "$opt" in
        o)  host="$OPTARG";;
        p)  pass="$OPTARG";;
        u)  uname="$OPTARG";;
        d)  base="$OPTARG";;
        i)  projectid="$OPTARG";;
        s)  sessions="$OPTARG";;
        t)  scantypes="$OPTARG";;
        f)  format="$OPTARG";;
        x)  overwrite=1;;
        h)  usage
            exit;;
        ?)  # Unknown flag
            usage
            exit 1;;
    esac
done

shift `expr $OPTIND - 1`

if [[ $OPTIND -le 1 ]]; then #no arguments
    usage
    exit 1
fi

if [[ -z $host ]]; then
    usage
    echo -e "\nPlease specify your XNAT host URL to -o flag.\n"
    exit 1
fi
host=${host%/} #strip any trailing slashes

if [[ -z $base ]]; then
    usage
    echo -e "\nPlease specify an output directory to -d flag.\n"
    exit 1
fi

if [[ -z $projectid ]]; then
    usage
    echo -e "\nPlease specify a XNAT project ID to the -p flag.\n"
    exit 1
fi

if [[ -n $format ]]; then
    format="resources/$format/"
fi

#make base dir
mkdir -p $base
if [[ ! -d $base ]]; then
    echo -e "\nCannot create output directory $base. Please specify a valid output directory to -d flag."
    exit 1
fi

#make sure base dir has full path
if [[ ${base:0:1} != "/" ]]; then
    base=`pwd`/$base
fi

#get username and password if not given in argument list
if [[ -z $uname ]]; then
    echo -n "XNAT Username: "
    read uname
fi
if [[ -z $pass ]]; then
    stty_orig=`stty -g`
    stty -echo
    echo -n "XNAT Password: "
    read pass
    stty $stty_orig
fi

cd $base
mkdir -p $base/XNAT_metadata


function login(){
    local url="$host/data/JSESSION"
    if [[ -n $jses ]]; then
        curl --cookie JSESSIONID=$jses "$url" -X DELETE >/dev/null 2>&1
    fi
    jses=`curl -u $uname:$pass "$url" -X POST 2>/dev/null`
}
login

echo -e "\nRetrieving all MR sessions for project $projectid...\n"
sessionfile=$base/XNAT_metadata/mrsessions_`date +\%Y\%m\%d`.csv
curl --cookie JSESSIONID=$jses -X GET \
    "$host/data/archive/projects/$projectid/experiments?xsiType=xnat:mrSessionData&format=csv&columns=ID,label,xnat:subjectData/label" \
    2>/dev/null | tr -d '[:blank:]' | tr -d \" > $sessionfile

tmp=`wc -l $sessionfile | awk '{print $1}'`
if [[ $tmp -lt 2 ]]; then
    msg="The curl command is failing, please make sure you entered a valid projectid ($projectid) "
    msg+="and that your username and password are correct. You can try running \"cat $sessionfile\" "
    msg+="to debug."
    echo $msg 1>&2
    exit 1
fi
echo -e "Done.\n"

if [[ -z $sessions ]]; then
    ses_list=( `awk -F',' 'NR>1 {print $5}' $sessionfile` )
else
    ses_list=( `echo $sessions | tr ',' ' '` )
fi

pushd $base > /dev/null
for label in ${ses_list[@]}; do
    each=`awk -F',' -v ses=$label '$5==ses {print}' $sessionfile`
    id=`echo $each | awk -F ',' '{print $1}'`
    if [[ -z $id ]]; then
        echo "Cannot find a session with label $label"
        continue
    fi
    #slabel=`echo $each | awk -F ',' '{print $3}'`

    #download from XNAT
    echo -e "Downloading images directories for $label:\n"
    for scantype in $scantypes; do
        zipfile=$label.$scantype.scans.zip
        #check for data locally (skip if already downloaded)
        if [[ -d $base/$label && $overwrite -eq 0 ]]; then
            echo -e "$base/$label directory exists, assuming data downloaded previously.\n"
            continue
        fi

        cmd="curl --cookie JSESSIONID=$jses -X GET \"$host/data/experiments/$id/scans/$scantype/${format}files?format=zip&structure=legacy\" > $zipfile"
        eval $cmd
        zip -T $zipfile
        if [[ $? -ne 0 ]]; then
            login
            eval $cmd
            zip -T $zipfile
            if [[ $? -ne 0 ]]; then
                echo "Issue downloading $label $id, see `pwd`/$zipfile" 1>&2
                continue
            fi
        fi
        unzip $zipfile
        if [[ $? -ne 0 ]]; then
            echo "The curl download is failing for $label (type=$scantype). You can try running \"cat $(pwd)/$zipfile\" to debug." 1>&2
            exit 1
        else
            rm $zipfile
        fi
    done
    echo -e "Done.\n"
done
popd > /dev/null
curl --cookie JSESSIONID=$jses "$host/data/JSESSION" -X DELETE >/dev/null 2>&1
