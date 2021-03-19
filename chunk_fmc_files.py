
import os.path
import numpy as np
import argparse
from glob import glob
from datetime import datetime, timedelta
import xarray as xr
import uuid
import shutil
import sys
from osgeo import gdal 
from matplotlib import pyplot as plt
import netCDF4
import json


fmc_stack_path = "/g/data/ub8/au/FMC/c6/mosaics/fmc_c6_{}.nc"


#def pack_fmc_mosaic_chunks(dates, fmc_mean, fmc_stdv, q_mask, dest):
def pack_fmc_mosaic_chunks(dates, fmc_mean, dest):
    lat_max = -10.
    lat_min = -44.
    lon_max = 154.
    lon_min = 113.
    res = 0.005
    
    x_size = int((lon_max - lon_min)/res)
    y_size = int((lat_max - lat_min)/res)
    
    with netCDF4.Dataset(dest, 'w', format='NETCDF4_CLASSIC') as ds:
        with open('nc_metadata.json') as data_file:
            attrs = json.load(data_file)
            for key in attrs:
                setattr(ds, key, attrs[key])
        setattr(ds, "date_created", datetime.now().strftime("%Y%m%dT%H%M%S"))
        
        t_dim = ds.createDimension("time", len(dates))
        x_dim = ds.createDimension("longitude", x_size)
        y_dim = ds.createDimension("latitude", y_size)

        var = ds.createVariable("time", "f8", ("time",))
        var.units = "seconds since 1970-01-01 00:00:00.0"
        var.calendar = "standard"
        var.long_name = "Time, unix time-stamp"
        var.standard_name = "time"
        var[:] = netCDF4.date2num(dates, units="seconds since 1970-01-01 00:00:00.0", calendar="standard")

        var = ds.createVariable("longitude", "f8", ("longitude",))
        var.units = "degrees"
        var.long_name = "longitude"
        var.standard_name = "longitude"
        var[:] = np.linspace(lon_min, lon_max-res, num=x_size)
        
        var = ds.createVariable("latitude", "f8", ("latitude",))
        var.units = "degrees"
        var.long_name = "latitude"
        var.standard_name = "latitude"
        var[:] = np.linspace(lat_max, lat_min+res, num=y_size)
        
        var = ds.createVariable("fmc_mean", 'f4', ("time", "latitude", "longitude"), fill_value=-9999.9, chunksizes=(len(dates),50,50))
        var.long_name = "Mean Live Fuel Moisture Content"
        var.units = '%'
        var[:] = fmc_mean[...]

        #var = ds.createVariable("fmc_stdv", 'f4', ("time", "latitude", "longitude"), fill_value=-9999.9, chunksizes=(len(dates),50,50))
        #var.long_name = "Standard Deviation Live Fuel Moisture Content"
        #var.units = '%'
        #var[:] = fmc_stdv[...]
        
        #var = ds.createVariable("quality_mask", 'i1', ("time", "latitude", "longitude"), fill_value=0, chunksizes=(len(dates),50,50))
        #var.long_name = "Quality Mask"
        #var.units = 'Cat'
        #var[:] = q_mask[...]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Modis Vegetation Analysis argument parser""")
    parser.add_argument('-y', '--year', type=int, required=True, help="Year of data.")
    parser.add_argument('-c', '--compression', action='store_true', help="Apply compression to destination netCDF4.")
    parser.add_argument('-dst', '--destination', required=True, type=str, help="Full path to destination.")
    args = parser.parse_args()


    unchunked_fmc = xr.open_dataset(fmc_stack_path.format(args.year))
    fmc_dates = unchunked_fmc.time.data
    print(fmc_dates)
    fmc_dates = [datetime.utcfromtimestamp(d.astype('O')/1e9) for d in fmc_dates]
    fmc_mean = unchunked_fmc.fmc_mean.data
    print('fmc_mean')
    #fmc_stdv = unchunked_fmc.fmc_stdv.data
    #print('fmc_stdv')
    #q_mask = unchunked_fmc.quality_mask.data
    #print('q_mask')

    #pack_fmc_mosaic_chunks(fmc_dates, fmc_mean, fmc_stdv, q_mask, args.destination)
    pack_fmc_mosaic_chunks(fmc_dates, fmc_mean, args.destination)
    del fmc_mean






