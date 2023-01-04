#!/bin/bash


export KEEPDATA=YES
export machine=WCOSS2
export USHverif_global=/lfs/h2/emc/ens/noscrub/xianwu.xue/VERIFY_GEFS/EMC_verif-global/ush
export DATA=/lfs/h2/emc/stmp/xianwu.xue/verif_global_standalone_ctl_rpl_c00_g2g_step2_20190506_20201130_para/tmp/verif_global.244246

export NET=verif_global
export RUN=grid2grid_step2
export QUEUESERV=dev_transfer
export ACCOUNT=GEFS-DEV
export PARTITION_BATCH=
export webhost=emcrzdm.ncep.noaa.gov
export webhostid=xianwu.xue
export webdir=/home/people/emc/www/htdocs/gmb/xianwu.xue/METplus/replay_ctl_rpl_c00_all_para

python $USHverif_global/build_webpage.py
