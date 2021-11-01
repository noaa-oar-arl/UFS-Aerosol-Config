#!/usr/bin/env python
"""

This function is create FV3 cubed sphere intial conditions for UFS-Aerosols.  
It uses the scipy.interpolate.interp1d function for vertical interpolation and 
ESMF bilinear interpolation via xesmf for horizontal interpolation.  

"""

import xarray as xr
import numpy as np
import xesmf as xe
import fv3grid as fg
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os
import netCDF4

def horizontal_interp(source,target,method='bilinear'):
    """regrid horizontally using a bilinear interpolation"""
    R = xe.Regridder(source,target,method)
    out = R(source)
    return out

def vertical_interp(source,source_plevs,target_plevs):
    """ interpolate with logP using a cubic spline"""
    source['lev'] = source_plevs
    out = source.interp(lev=target_plevs[1:],method='linear')
    return out

def get_merra2_plevs():
    """
    Generates the MERRA2 pressure levels using 1000 mb as the surface.
    """
    merra_ak = np.array([ 1, 2.00000023841858, 3.27000045776367, 4.75850105285645,
                          6.60000133514404, 8.93450164794922, 11.9703016281128, 15.9495029449463,
                          21.1349029541016, 27.8526058197021, 36.5041084289551, 47.5806083679199,
                          61.6779098510742, 79.5134124755859, 101.944023132324, 130.051025390625,
                          165.079025268555, 208.497039794922, 262.021057128906, 327.64306640625,
                          407.657104492188, 504.680114746094, 621.680114746094, 761.984191894531,
                          929.294189453125, 1127.69018554688, 1364.34020996094, 1645.71032714844,
                          1979.16040039062, 2373.04052734375, 2836.78051757812, 3381.00073242188,
                          4017.541015625, 4764.39111328125, 5638.791015625, 6660.34130859375,
                          7851.2314453125, 9236.572265625, 10866.3017578125, 12783.703125,
                          15039.302734375, 17693.00390625, 20119.201171875, 21686.501953125,
                          22436.30078125, 22389.80078125, 21877.59765625, 21214.998046875,
                          20325.8984375, 19309.6953125, 18161.896484375, 16960.896484375,
                          15625.99609375, 14290.9951171875, 12869.59375, 11895.8623046875,
                          10918.1708984375, 9936.521484375, 8909.9921875, 7883.421875,
                          7062.1982421875, 6436.263671875, 5805.3212890625, 5169.61083984375,
                          4533.90087890625, 3898.20092773438, 3257.08081054688, 2609.20068359375,
                          1961.310546875, 1313.48034667969, 659.375244140625, 4.80482578277588, 0])
    
    merra_bk = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8.17541323527848e-09,
                         0.00696002459153533, 0.0280100405216217, 0.0637200623750687,
                         0.113602079451084, 0.156224086880684, 0.200350105762482,
                         0.246741116046906, 0.294403105974197, 0.343381136655807,
                         0.392891138792038, 0.44374018907547, 0.494590193033218,
                         0.546304166316986, 0.581041514873505, 0.615818440914154,
                         0.650634944438934, 0.685899913311005, 0.721165955066681,
                         0.749378204345703, 0.770637512207031, 0.791946947574615,
                         0.81330394744873, 0.834660947322845, 0.856018006801605,
                         0.877429008483887, 0.898908019065857, 0.920387029647827,
                         0.941865026950836, 0.963406026363373, 0.984951972961426, 1])

    phalf_merra = (merra_ak + merra_bk * 100000.)/ 100.
    return phalf_merra

def get_fv3_plevs(gfs_ctrl,return_akbk=False):
    """
    Return the FV3 pressure levels using the fv3_core file and 1000 mb as the surface.
    """
    ak = gfs_ctrl.vcoord.values[0,:]

    bk = gfs_ctrl.vcoord.values[1,:]

    phalf_fv3 = (ak + bk * 100000.)/ 100.
    
    if return_akbk:
        return ak,bk
    else:
        return phalf_fv3


def open_dataset(filename):
    dset = xr.open_dataset(filename,decode_cf=True,mask_and_scale=False,decode_times=False)
    return dset


def main():
    parser = ArgumentParser(description='Regrid MERRA2 to FV3 native netcdf input files', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m', '--merra_file', help='input merra2 3d file', type=str, required=True)
    parser.add_argument('-c', '--core_file', help='fv3 core tile file: example gfs_ctrl.nc', default=None, required=True)
    parser.add_argument('-t', '--tracer_file', help='fv3 tile tracer file: example gfs_data.tile1.nc', default=None, required=True)
    parser.add_argument('-r', '--resolution', help='fv3 grid resolution: example C384', default=None, required=True)
#    parser.add_argument('-g', '--grid_spec', help ='fv3 grid_spec file: example grid_spec.tile1.nc', default=None, required=True) 
    parser.add_argument('-a', '--aerosol', help='True: aerosol file.... False: Gas', default=True, required=False)
    args = parser.parse_args()

    merra_file = args.merra_file
    core_file = args.core_file
    tracer_file = args.tracer_file
#    grid = args.grid_spec

    # open files
    merra = open_dataset(merra_file).isel(time=0) # only get the first time stamp
    core = open_dataset(core_file)
    tracer = open_dataset(tracer_file)

    tile = int(tracer_file.split('.')[1].strip('tile'))
    grid = fg.get_fv3_grid(res=args.resolution,tile=tile) # open_dataset(grid)

    #reformat grid file for interpolation
#    grid = grid.set_coords(['grid_lont','grid_latt']).area
    #grid = grid.rename({"grid_yt":'y','grid_xt':'x','grid_lont':'lon','grid_latt':'lat'})
    grid.x.attrs = {}
    grid.y.attrs = {} 
    grid.lat_b.attrs = {}
    grid.lon_b.attrs = {}
    grid.x_b.attrs = {}
    grid.y_b.attrs = {}
    # choose MERRA2 aerosol files
    ntracers = 3
    if args.aerosol:
        merra_2_aerosols = ['BCPHILIC','BCPHOBIC','DMS',
                            'DU001','DU002','DU003','DU004','DU005',
                            'OCPHILIC','OCPHOBIC','SO2','SO4',
                            'SS001','SS002','SS003','SS004','SS005','MSA']
        merra = merra[merra_2_aerosols]
        rename_dict = dict(BCPHILIC='bc2',BCPHOBIC='bc1',DMS='dms',
                           DU001='dust1',DU002='dust2',DU003='dust3',DU004='dust4', DU005='dust5',
                           SS001='seas1',SS002='seas2',SS003='seas3',SS004='seas4', SS005='seas5',
                           OCPHILIC='oc2',OCPHOBIC='oc1',SO2='so2',SO4='so4',MSA='msa')
        fv3_units = dict(so2='ppm',so4='ug/kg',dms='ppm',msa='ppm',bc2='ug/kg',bc1='ug/kg',
                         dust1='ug/kg',dust2='ug/kg',dust3='ug/kg',dust4='ug/kg',dust5='ug/kg',
                         seas1='ug/kg',seas2='ug/kg',seas3='ug/kg',seas4='ug/kg',seas5='ug/kg',
                         oc1='ug/kg',oc2='ug/kg')

        merra = merra.rename(rename_dict)
        ntracers += len(merra_2_aerosols)
        
    # get plevs 
    fv3_press = get_fv3_plevs(core)
    merra_press = get_merra2_plevs()[1:]

    # interpolate horizontally 
    hinterped = horizontal_interp(merra,grid,method='bilinear')
    
    # vertically interpolate 
    hvinterped = vertical_interp(hinterped, np.log(merra_press), np.log(fv3_press))
    
    # construct 3d pressure
    p = np.ones(tracer.o3mr.shape)
    ak,bk = get_fv3_plevs(core, return_akbk=True)
    for i in range(tracer.o3mr.shape[1]):
        for j in range(tracer.o3mr.shape[2]):
            p[:,i,j] = ak[1:] + bk[1:] * 101325.0
    d = p / (287 * tracer.t)

    for i in rename_dict:
        field = rename_dict[i]
        # copy fv3 o3mr to new field
        tracer[field] = tracer.o3mr.copy()
        tracer[field].attrs['long_name'] = field
        tracer[field][:,:,:] = hvinterped[field].data[:,:,:] # convert to kg/kg
        tracer[field] = tracer[field].fillna(0.)

    # convert units:
    for i in fv3_units:
        if fv3_units[i] == 'ug/kg':
            # this just a quick conversion from kg/kg to ug/kg 
            tracer[i] = tracer[i] * 1e9

        elif fv3_units[i] == 'ppm':
            if i == 'dms': 
                mw = 63.15
            if i == 'so2':
                mw = 64.066
            if i == 'msa':
                mw = 96.11
            # convert
            tracer[i] = tracer[i] * d * 1e6 * 24.45 / mw

        tracer[i].attrs['units'] = fv3_units[i]

    # move old tracer file 
    os.rename(tracer_file, tracer_file.replace('.nc','.nc.old'))

    # output to original tracer file name
    tracer.to_netcdf(tracer_file)    
    
    #note that we need to add ntracer back into the file (standard UFS has 3 tracers) 
    base_file = netCDF4.Dataset(tracer_file, "r+")
    base_file.createDimension("ntracer", ntracers)
    

if __name__ == "__main__":
        main()
