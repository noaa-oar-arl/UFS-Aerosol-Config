# MERRA2 ICs

This is a utility to create MERRA2 ICs for a given resolution of UFS-Aerosols allowing to start from a "warm" state.

The MERRA2 file needed can be found here: https://disc.gsfc.nasa.gov/datasets/M2I3NVAER_5.12.4/summary?keywords=MERRA-2%203d

### Requirements

python modules:
- xesmf
- xarray
- netcdf4 
- numpy
- fv3 grid (https://github.com/noaa-oar-arl/fv3grid)

## How To Use

There is a bash script `add_merra2_day.sh` that is be used that will process the ICs for a given day.  

If the days are available already on HPSS (/NCEPDEV/emc-naqfc/5year/Barry.Baker/MERRA2_INST_3D_AERO/) then the file will be downloaded automatically.  If not 
please modify the file appropriately to point to the specific file path.

first cd to your COM directory after the initial get GFS ICs job completes. Then

```bash 
./add_merra2_day.sh YYYYMMDD
```

where `YYYYMMDD` is the initial start date.  

