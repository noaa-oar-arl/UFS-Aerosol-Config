#!/bin/bash


ml hpss

for yyyy in 2013 2016 2018; do
    for mm in 01 07; do
	for dd in 01 15; do
	    #create some variables for later
	    yyyymmddhh=${yyyy}${mm}${dd}00
	    yyyymmdd=${yyyy}${mm}${dd}
	    
	    # just a print statement
	    echo ${yyyymmddhh}
	    
	    # enter directory
	    pushd ${yyyymmddhh}/gfs/C384/INPUT

	    # copy python file
	    cp /scratch2/NAGAPE/arl/Barry.Baker/UFS_AERO_CONFIGS/develop/utils/merra2_to_fv3_cubesphere.py .
	    
	    # grab MERRA2 from HPSS
	    htar -xvf /NCEPDEV/emc-naqfc/5year/Barry.Baker/MERRA2_INST_3D_AERO/MERRA2_400.inst_3d_aero_Nv.${yyyy}.nc4 MERRA2_400.inst3_3d_aer_Nv.${yyyymmdd}.nc4
	    
	    # Modify the GFS files for UFS-Aersols with MERRA2 ICs
	    for i in {1..6}; do 
		./merra2_to_fv3_cubesphere.py -m MERRA2_400.inst3_3d_aer_Nv.${yyyymmdd}.nc4 -c gfs_ctrl.nc -t gfs_data.tile${i}.nc -r C384
	    done
	    
	    # go back to base directory 
	    popd
	done
    done
done
