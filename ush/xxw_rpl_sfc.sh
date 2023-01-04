#!/bin/bash


module load prod_util/2.0.13

mondays=""
# For Monday
fstart=2019051300 #2019050600
fend=2020113000
finc1=$((7*24))
fhcnt=$fstart
while [[ $fhcnt -le $fend ]];
do
    mondays="${mondays} $fhcnt"
    fhcnt=$($NDATE $finc1 $fhcnt)
done

#echo $mondays

# for Thurdays
thursdays=""
fstart=2019051600 #2019050900
fend=2020112600 # 2020112600
finc1=$((7*24)) #$((14*24))

fhcnt=$fstart
while [[ $fhcnt -le $fend ]];
do
    thursdays="${thursdays} $fhcnt"
    fhcnt=$($NDATE $finc1 $fhcnt)
done


#echo $mondays $thursdays
cd /lfs/h2/emc/ens/noscrub/xianwu.xue/VERIFY_GEFS/EMC_verif-global/ush

for fhcnt in $mondays $thursdays
do
    #echo $fhcnt
    yyyymmdd=$(echo ${fhcnt} | cut -c1-8)
    echo $yyyymmdd

    export xxwdate=$yyyymmdd; ./run_verif_global.sh ../parm/config/config.rpl_c00_step01 
done
