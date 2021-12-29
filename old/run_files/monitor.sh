#!/bin/bash

usage()
{
  echo -en "\nSYNTAX ERROR:\n\n"
  echo "usage: $0 -d dept -p project_id"
  echo -en "\nExample:\n$0 -d nyspi -p testproject\n\n"
}

if [ "$1" == "" ]; then usage;exit 1;fi
if [[ $# -eq 1 ]]; then usage;exit 1;fi
if [[ $# -lt 3 ]]; then usage;exit 1;fi

while [ "$1" != "" ]; do
    case $1 in
        -d )           shift
                       dept=$1
                       ;;
        -p )           shift
                       projid=$1
                       ;;
        * )            usage
                       exit 1
    esac
    shift
done

clear
echo
echo -e "\e[41;38;5;231m BIDSPREP \e[231;48;5;19m MANAGEMENT \e[0m"
echo

admin="juan"

if ! $( docker service ls | grep -q ${dept}_${projid}); then
   echo -en "\nNo active or inactive jobs running for ${dept}_${projid}\n\n"
   exit 1
elif ! $( id -a | egrep -q "${admin}|${projid}" ); then
   echo -en "\nYou are not authorized to manage project ${dept}_${projid}.\n\n"
   exit 1
fi

yelcol()
{
printf '\e[33m' '\e[0m'
}

grecol()
{
printf '\e[32m' '\e[0m'
}

redcol()
{
printf '\e[31m' '\e[0m'
}

#### function to list the job ####
joblist()
{
yelcol
echo -en "\n\e[1mCURRENT ACTIVE & INACTIVE JOBS FOR PROJECT \e[32m$projid\e[0m\n\n"
echo -en "\n  \e[4m\e[1m\e[33mStatus\e[0m       \e[1m\e[4m\e[33mJob Name\e[0m\n"

for job in `docker service ls | awk '{print $2}' | grep ${dept}_${projid}`
do
	if ! [ $(docker service ps $job -f "desired-state=running" -q | wc -l) == 0 ]; then
		echo "  Active  -->  ${job}"
	else
		echo "Inactive  -->  ${job}"
	fi
done
echo
}

#### function to list the options ####
optlist()
{
yelcol
echo -e "\e[1mAvailable management options:\e[0m"

PS3="
(Press Ctrl+C to abort)

Select an option: "
select option in "Check Logs" "Save Logs" "Remove Jobs" "Refresh" "Exit"
do
break
done
}

##### option functions #####
check_logs()
{
read -p "Enter the job name to check the logs: " jobname

if [[ "$jobname" == "" ]]; then
redcol
echo -e "\e[1mInvalid input\e[0m"
exit 1
fi

grecol
echo -en "Loading...\e[0m\n"
sleep 1
docker service logs $jobname --raw
echo
}

save_logs()
{
echo
grecol
echo -e "\e[1mSave Logs\e[0m"
read -p "ENTER JOB NAME: " jobname
read -p "ENTER FULL PATH OF LOG FILE: " logfile

if [[ "$jobname" == "" ]]; then
redcol
echo -e "\e[1mInvalid job name\e[0m"
exit 1
fi

if ! [[ "$logfile" =~ ^/ ]]; then
redcol
echo -e "\e[1mInvalid log filename\e[0m"
exit 1
fi

grecol
echo -en "Saving...\e[0m\n"
sleep 1
docker service logs $jobname --raw > $logfile 2>&1
if [ $? -eq 0 ]; then
echo "Logs saved to $logfile"
else
redcol
echo -e "\e[1mSave FAILED. Either permission denied or incorrect path\e[0m"
fi
echo
}


remove_jobs()
{
read -p "Enter the job name to remove, or enter 'all': " jobname
if [[ "$jobname" == "all" ]]; then
        #for all in `docker service ls | grep $projid | awk '{print $2}'`
        for all in `docker service ls | awk '{print $2}' | grep ${dept}_${projid}`
        do
                echo "Removing:"
                docker service rm $all
                echo
        done
else
        echo "Removing:"
        docker service rm $jobname
fi
echo
}

refreshjobs()
{
$0 -d ${dept} -p ${projid}
}

exitnow()
{
echo "Good Bye"
exit
}


##########################
#### Actual process ####

joblist && optlist
arg=`echo "$option" | sed -r 's/ /_/g'`

if [[ "$arg" == "Check_Logs" ]]; then
check_logs
fi

if [[ "$arg" == "Save_Logs" ]]; then
save_logs
fi

if [[ "$arg" == "Remove_Jobs" ]]; then
remove_jobs
fi

if [[ "$arg" == "Refresh" ]]; then
refreshjobs
fi

if [[ "$arg" == "Exit" ]]; then
exitnow
fi