
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


flam_stack_path = "/g/data/ub8/au/FMC/mosaics/flam_c6_{}.nc"


#def pack_flammability_mosaic_chunks(dates, flam, anom, q_mask, dest):
def pack_flammability_mosaic_chunks(dates, flam, dest):
    lat_max = -10.
    lat_min = -44.
    lon_max = 154.
    lon_min = 113.
    res = 0.005
    
    x_size = int((lon_max - lon_min)/res)
    y_size = int((lat_max - lat_min)/res)
    t_size = len(dates)
    
    with netCDF4.Dataset(dest, 'w', format='NETCDF4_CLASSIC') as ds:
        with open('nc_metadata.json') as data_file:
            attrs = json.load(data_file)
            for key in attrs:
                setattr(ds, key, attrs[key])
        setattr(ds, "date_created", datetime.now().strftime("%Y%m%dT%H%M%S"))
        
        t_dim = ds.createDimension("time", len(dates))
        x_dim = ds.createDimension("longitude", x_size)
        y_dim = ds.createDimension("latitude", y_size)

        var = ds.createVariable("time", "f8", ("time",), chunksizes=(t_size,))
        var.units = "seconds since 1970-01-01 00:00:00.0"
        var.calendar = "standard"
        var.long_name = "Time, unix time-stamp"
        var.standard_name = "time"
        var[:] = netCDF4.date2num(dates, units="seconds since 1970-01-01 00:00:00.0", calendar="standard")

        var = ds.createVariable("longitude", "f8", ("longitude",), chunksizes=(50,))
        var.units = "degrees"
        var.long_name = "longitude"
        var.standard_name = "longitude"
        var[:] = np.linspace(lon_min, lon_max-res, num=x_size)
        
        var = ds.createVariable("latitude", "f8", ("latitude",), chunksizes=(50,))
        var.units = "degrees"
        var.long_name = "latitude"
        var.standard_name = "latitude"
        var[:] = np.linspace(lat_max, lat_min+res, num=y_size)
        
        var = ds.createVariable("flammability", 'f4', ("time", "latitude", "longitude"), fill_value=-9999.9, chunksizes=(t_size,50,50))
        var.long_name = "Flammability Index"
        var.units = '%'
        var[:] = flam[...]

        #var = ds.createVariable("anomaly", 'f4', ("time", "latitude", "longitude"), fill_value=-9999.9, chunksizes=(len(dates),50,50))
        #var.long_name = "FMC Anomaly"
        #var.units = '%'
        #var[:] = anom[...]
        
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

    unchunked_flam = xr.open_dataset(flam_stack_path.format(args.year))
    flam_dates = unchunked_flam.time.data
    print(flam_dates)
    flam_dates = [datetime.utcfromtimestamp(d.astype('O')/1e9) for d in flam_dates]
    flam = unchunked_flam.flammability.data
    print('flam')
    #anom = unchunked_flam.anomaly.data
    #print('anom')
    #q_mask = unchunked_flam.quality_mask.data
    #print('q_mask')

    #pack_flammability_mosaic_chunks(flam_dates, flam, anom, q_mask, args.destination)
    pack_flammability_mosaic_chunks(flam_dates, flam, args.destination)
    del flam
