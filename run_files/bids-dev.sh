#!/bin/bash



###### BEGIN ########
#Usage message to display
usage()
{
  echo -en "\nSYNTAX ERROR\n"
  echo -e "usage: $0 [ -d directory -p project_id -a arguments ]\n"
  echo -e "Where directory is before the projects\n"
  echo -en "[arguments] can be:\n
Individual:
            [pull] - Download bids into rawdata
           [split] - Split multivolume data.
          [intend] - Apply intendedFor and taskName
           [valid] - Run bids validator.

Combined:
     [pulltosplit] - pull + split
    [pulltointend] - pull + intend
     [pulltovaild] - pull + vaild
   [splittointend] - split + intend
    [splittovalid] - split + intend + valid
   [intendtovalid] - intend + valid\n\n"
}
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



#List of acceptable arguments
listofarg="
pull
split
intend
valid
pulltosplit
pulltointend
pulltovalid
splittointend
splittovalid
intendtovalid
"


totalarg=`echo $listofarg | sed 's/ /|/'g`

if  [[ "$arg"  != $(totalarg)  ]]; then
        echo -en "\nERROR: INCORRECT ARGUMENT\n"
        usage
        exit 1
fi
############################################


while [ "$1" != "" ]; do
    case $1 in
        -d )           shift
                       dept=$1
                       ;;
        -p )           shift
                       project_id=$1
                       ;;
        -a)            shift
                       arg=$1
                       ;;
        * )            usage
                       exit 1
    esac
    shift
done

#############################################


#####################################
# DEFINED FUNCTIONS #
#####################################

pull()
{
/usr/local/pipeline/bids-dev-setup/scripts/xnatpull-cp.sh ${project_id}
}

####

#split()
#{
#}

####

#intend()
#{
#/intend.sh ${projid} ${subjid} ${exam}
#}

####

#validator()
#{
#}

####

##################


#####################################
# ACTUAL PROCECSS #
#####################################

if [[ "$arg" == "pull" ]]; then
pull
fi

if [[ "$arg" == "split" ]]; then
split
fi


if [[ "$arg" == "intend" ]]; then
intend
fi


if [[ "$arg" == "valid" ]]; then
validator
fi



if [[ "$arg" == "pulltosplit" ]]; then
pull \
&& split
fi


if [[ "$arg" == "pulltointend" ]]; then
pull \
&& split \
&& intend
fi


if [[ "$arg" == "pulltovalid" ]]; then
pull \
&& splittop \
&& intend \
&& validator
fi


if [[ "$arg" == "splittovalid" ]]; then
split \
&& intend \
&& validator
fi



if [[ "$arg" == "intendtovalid" ]]; then
intend \
&& validator
fi

#################################################

