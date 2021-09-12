#!/bin/bash
#
# Shortcut script to launch cluster FMRIPREP container
#
# docker -H muldermri.nyspi.local run --rm --cpus=8 -v /HORGA_DATA/mnt/sda1/7655_neuromelanin_CHR/7655_MRI_data/Nifti:/input -v /HORGA_DATA/mnt/sda1/7655_neuromelanin_CHR/7655_MRI_data/fmriout:/output  -v /usr/local/clustsub/freesurfer-license.txt:/opt/freesurfer/license.txt:ro fmri:nyspimri /input /output participant | tee fmriout-pipeline.out 2>&1
#
usage()
{
  echo "usage: $0 [-i bids_input_base_directory -o output_directory -l console_log_file] | [-h] "
}
# ############################## #
# ########### MAIN ############# #
# ############################## #
if [ "$1" == "" ]; then
  usage
  exit 1
fi

if [[ $# -eq 1 ]]; then
  usage
  exit
fi

if [[ $# -lt 6 ]]; then
  usage
  exit 1
fi
while [ "$1" != "" ]; do
    case $1 in
        -i )           shift
                       indir=$1
                       ;;
        -o )           shift
                       outdir=$1
                       ;;
        -l )           shift
                       log=$1
                       ;;
        * )            usage
                       exit 1
    esac
    shift
done
#
# Could error check for volumes being available and such
echo Launching FMRPREP pipelines on $indir . Output will be written to $outdir . Job can be sent to background. Console output written locally to $log
fpath=`echo $indir | sed -r 's/\//_/g'| grep -o '.\{10\}$'`
nohup /usr/bin/docker service create  \
--replicas 1 \
--reserve-cpu 8 \
--reserve-memory 16g \
--mode replicated \
--name=fmri-`id -un`$fpath \
--mount type=bind,source=$indir,destination=/input,readonly=true \
--mount type=bind,source=$outdir,destination=/output \
--mount type=bind,source=/MRI_DATA/freesurferlicense.txt,destination=/opt/freesurfer/license.txt,readonly=true \
nipreps/fmriprep:21.0.0rc0 \
/input /output participant \
--output-spaces MNI152NLin2009cAsym:res-2 MNI152NLin2009cAsym:res-native \
> $log 2>&1 &
    esac
    shift
done
