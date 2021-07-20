#!/bin/bash

####
# This bash script will copy the initial condition input for a given day to the directory ready for 
# the coupled crow repository.  Note that for this to work it needs to be in a folder called: 
#
# FV3ICS and your yaml file should point to 
#
# PATH_TO_DIRECTORY/FV3ICS/..
###

#load hpss
ml hpss/hpss

date=${1}

yyyy=`date --date=${1} "+%Y"`
mm=`date --date=${1} "+%m"`
dd=`date --date=${1} "+%d"`

yyyymmddhh=`date --date=${1} "+%Y%m%d00"`

mkdir -p ${yyyymmddhh}
pushd ${yyyymmddhh}

htar -xvf /BMC/fim/5year/FV3_ICs_GFS/${yyyy}/${mm}/${yyyymmddhh}_C384.tar
