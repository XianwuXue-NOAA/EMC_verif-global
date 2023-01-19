#!/bin/bash

./run_verif_global.sh ../parm/config/config.rpl_c00_step01 

./run_verif_global.sh ../parm/config/config.rpl_c00_step02



./run_verif_global.sh ../parm/config/config.gfs_step01

./run_verif_global.sh ../parm/config/config.gfs_step02

./run_verif_global.sh ../parm/config/config.ctl_c00_step01


export xxwdate=20190610; ./run_verif_global.sh ../parm/config/config.rpl_c00_step01

20190617 ..


export xxwdate=20190506; ./run_verif_global.sh ../parm/config/config.rpl_c00_sfc_step01


./run_verif_global.sh  ../parm/config/config.replay_ctl_rpl_step02

./run_verif_global.sh  ../parm/config/config.replay_ctl_rpl_all_step02 


#-----
./run_verif_global.sh ../parm/config/config.ctl_c00_step01

./run_verif_global.sh  ../parm/config/config.replay_ctl_rpl_all_step02
