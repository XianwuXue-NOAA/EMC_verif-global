#!/bin/sh
# Program Name: precip_step1
# Author(s)/Contact(s): Mallory Row
# Abstract: Run METplus for global precipitation verification
#           to produce CTC stats
# History Log:
#   2/2019: Initial version of script
# 
# Usage:
#   Parameters: 
#       agrument to script
#   Input Files:
#       file
#   Output Files:  
#       file
#  
# Condition codes:
#       0 - Normal exit
# 
# User controllable options: None

#set -x

# Set up directories
mkdir -p $RUN
cd $RUN

# Set up environment variables for initialization, valid, and forecast hours and source them
export precip1_type_list="${precip1_obtype}_accum${precip1_accum_length}hr"
if [ $precip1_fhr_max -gt 180 ]; then
    export precip1_fhr_max=180
fi
python $USHverif_global/set_init_valid_fhr_info.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran set_init_valid_fhr_info.py"
echo
. $DATA/$RUN/python_gen_env_vars.sh
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully sourced python_gen_env_vars.sh"
echo

# Link needed data files and set up model information
mkdir -p data
python $USHverif_global/get_data_files.py
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran get_data_files.py"
echo

# Create output directories for METplus
python $USHverif_global/create_METplus_output_dirs.py
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran create_METplus_output_dirs.py"
echo 

# Create job scripts to run METplus
python $USHverif_global/create_METplus_job_scripts.py
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran create_METplus_job_scripts.py"

# Run METplus job scripts
chmod u+x metplus_job_scripts/job*
ncount=$(ls -l  metplus_job_scripts/job* |wc -l)
nc=0;iproc=0; node=1; rank=0
while [ $nc -lt $ncount ]; do
    if [ $MPMD = YES ];then
        if [ $iproc -ge $nproc ]; then iproc=0; rank=0; node=$((node+1)); fi
        poe_script=$DATA/$RUN/metplus_job_scripts/poe_jobs_node${node}
        if [ $iproc -eq 0 ]; then
            rm -f $poe_script; touch $poe_script
        fi
        nc=$((nc+1))
        iproc=$((iproc+1))
        if [ $machine = THEIA ]; then
            echo "$rank $DATA/$RUN/metplus_job_scripts/job${nc}" >>$poe_script
            rank=$((rank+1))
        else
            echo "$DATA/$RUN/metplus_job_scripts/job${nc}" >>$poe_script
        fi
        if [ $iproc -eq $nproc -o $nc -eq $ncount ]; then
            # if at final record and have not reached the 
            # final processor then write echo's to
            # poescript for remaining processors
            if [ $nc -eq $ncount ]; then
                while [ $iproc -lt $nproc ]; do
                    nc=$((nc+1))
                    iproc=$((iproc+1))
                    if [ $machine = THEIA ]; then
                        echo "$rank /bin/echo $iproc" >> $poe_script
                        rank=$((rank+1))
                    else
                        echo "/bin/echo $iproc" >> $poe_script
                    fi
                done
            fi
            chmod 775 $poe_script
            export MP_PGMMODEL=mpmd
            export MP_CMDFILE=${poe_script}
            if [ $machine = WCOSS_C ]; then
                launcher="aprun -j 1 -n ${iproc} -N ${iproc} -d 1 cfp"
            elif [ $machine = WCOSS_DELL_P3 ]; then
                launcher="mpirun -n $iproc cfp"
            elif [ $machine = THEIA ]; then
                launcher="srun --export=ALL --multi-prog"
            fi
            $launcher $MP_CMDFILE
            export err=$?
            if [ $err -ne 0 ]; then sh +x $poe_script ; fi
        fi
    else
        nc=$((nc+1))
        sh +x $DATA/$RUN/metplus_job_scripts/job${nc}
    fi
done

# Copy data to user archive or to COMOUT
gather_by=$precip1_gather_by
DATE=${start_date}
while [ $DATE -le ${end_date} ] ; do
    export DATE=$DATE
    export COMIN=${COMIN:-$COMROOT/$NET/$envir/$RUN.$DATE}
    export COMOUT=${COMOUT:-$COMROOT/$NET/$envir/$RUN.$DATE}
    mkdir -p $COMOUT
    for model in $model_list; do
        export model=$model
        for type in $precip1_type_list; do
            if [ $gather_by = VALID ]; then
                gather_by_hour_list=$precip1_vhr_list
            else
                gather_by_hour_list=$precip1_fcyc_list
            fi
            for gather_by_hour in $gather_by_hour_list; do
                if [ $gather_by = VSDB ]; then
                    valid_hr_end=$precip1_valid_hr_end
                    verif_global_filename="metplus_output/gather_by_$gather_by/stat_analysis/$type/$model/${model}_${DATE}${valid_hr_end}_${gather_by_hour}.stat"
                else
                    verif_global_filename="metplus_output/gather_by_$gather_by/stat_analysis/$type/$model/${model}_${DATE}${gather_by_hour}.stat"
                fi
                arch_filename="$arch_dir/metplus_data/by_$gather_by/precip/$type/${gather_by_hour}Z/$model/${model}_${DATE}.stat"
                comout_filename="$COMOUT/${model}_precip_${type}_${DATE}_${gather_by_hour}Z_${gather_by}.stat"
                if [ -s $verif_global_filename ]; then
                   if [ $SENDARCH = YES ]; then
                       mkdir -p $arch_dir/metplus_data/by_$gather_by/precip/$type/${gather_by_hour}Z/$model
                       cp $verif_global_filename $arch_filename
                   fi
                   if [ $SENDCOM = YES ]; then
                       cpfs $verif_global_filename $comout_filename
                       if [ "${SENDDBN^^}" = YES ]; then
                           $DBNROOT/bin/dbn_alert MODEL VERIF_GLOBAL $job $veif_global_filename
                       fi
                   fi
                else
                    err_exit "$verif_global_filename was not generated"
                fi
            done
        done
    done
    DATE=$(echo $($NDATE +24 ${DATE}00 ) |cut -c 1-8 )
done
