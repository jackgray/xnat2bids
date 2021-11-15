#!/bin/bash

ID=$1
exam=$2
logdir="/output"

## ID is subjID ##

echo -en "=================== RUNNING mv-split on: ${ID} ============================\n\n"

cd /output/sub-${ID}/ses-${exam}/fmap/ 

if [ ! -d /${logdir}/derivatives/convert/${ID}-tmp_dcm2bids/sub-${ID}_ses-${exam}/origFMAP ]; then
	mkdir -p /${logdir}/derivatives/convert/${ID}-tmp_dcm2bids/sub-${ID}_ses-${exam}/origFMAP
	cp * /${logdir}/derivatives/convert/${ID}-tmp_dcm2bids/sub-${ID}_ses-${exam}/origFMAP/.
fi

mkdir temp

for topup in *.nii.gz
do
	mv $topup temp/.
	cd temp
        
	fpe=`echo $topup | sed 's%mv%fpe%g'`
	rpe=`echo $topup | sed 's%mv%rpe%g'`
        fslsplit $topup tmp        
        mv tmp0001.nii.gz ../$fpe
        #fslswapdim tmp0000.nii.gz x -y z ../$rpe

	#testing new method of flip...
	fslorient -deleteorient tmp0000.nii.gz
    	fslswapdim tmp0000.nii.gz x -y z ../$rpe
   	fslcpgeom ../$fpe ../$rpe

        rm tmp*
	rm $topup
        #foreach json (`ls *mv_epi.json`)
        #cp $json `echo $json | sed 's%mv%rpe%g'`
        #mv $json `echo $json | sed 's%mv%fpe%g'` 

        cd ..
	
	json=`echo $topup | sed 's%nii.gz%json%g'`
	jsonfpe=`echo $fpe | sed 's%nii.gz%json%g'`
	jsonrpe=`echo $rpe | sed 's%nii.gz%json%g'`

# FIX THIS PART...

	 #cat $json | sed 's$func$ses-${exam}/func$g' > `echo $json`
	 mv $json $jsonfpe
         cat  $jsonfpe |  sed 's$"PhaseEncodingDirection": "j",$"PhaseEncodingDirection": "j-",$g' | sed 's$"PhaseEncodingPolarityGE": "Flipped",$"PhaseEncodingPolarityGE": "Unflipped",$g'  > `echo $jsonrpe`
         
                                
	
done  

chmod 775 *
rmdir temp

exit

echo -en "======================== COMPLETED mv-split ================================\n\n"
