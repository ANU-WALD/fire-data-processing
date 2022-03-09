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

def pack_fmc_mosaic_chunks(dates, fmc_mean, dest, t_chunk, lat_chunk, lon_chunk):
    
    lat_max = -10.
    lat_min = -44.
    lon_max = 154.
    lon_min = 113.
    res = 0.005
    
    lat_size = int((lat_max - lat_min)/res)
    lon_size = int((lon_max - lon_min)/res)
    t_size = len(dates)
    
    with netCDF4.Dataset(dest, 'w', format='NETCDF4_CLASSIC') as ds:
        with open('nc_metadata.json') as data_file:
            attrs = json.load(data_file)
            for key in attrs:
                setattr(ds, key, attrs[key])
        setattr(ds, "date_created", datetime.now().strftime("%Y%m%dT%H%M%S"))
        
        t_dim = ds.createDimension("time", t_size)
        x_dim = ds.createDimension("longitude", lon_size)
        y_dim = ds.createDimension("latitude", lat_size)

        var = ds.createVariable("time", "f8", ("time",), chunksizes=(t_chunk,))
        var.units = "seconds since 1970-01-01 00:00:00.0"
        var.calendar = "standard"
        var.long_name = "Time, unix time-stamp"
        var.standard_name = "time"
        var[:] = netCDF4.date2num(dates, units="seconds since 1970-01-01 00:00:00.0", calendar="standard")

        var = ds.createVariable("latitude", "f8", ("latitude",), chunksizes=(lat_chunk,))
        var.units = "degrees"
        var.long_name = "latitude"
        var.standard_name = "latitude"
        var[:] = np.linspace(lat_max, lat_min+res, num=lat_size)

        var = ds.createVariable("longitude", "f8", ("longitude",), chunksizes=(lon_chunk,))
        var.units = "degrees"
        var.long_name = "longitude"
        var.standard_name = "longitude"
        var[:] = np.linspace(lon_min, lon_max-res, num=lon_size)
        
        var = ds.createVariable("fmc_mean", 'f4', ("time", "latitude", "longitude"), fill_value=-9999.9, chunksizes=(t_chunk,lat_chunk,lon_chunk))
        var.long_name = "Mean Live Fuel Moisture Content"
        var.units = '%'
        var[:] = fmc_mean[...]




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Modis Vegetation Analysis argument parser""")
    parser.add_argument('-y', '--year', type=int, required=True, help="Year of data.")
    parser.add_argument('-dst', '--destination', required=True, type=str, help="Path to destination, without file name.")
    parser.add_argument('-t_chunk', '--time_chunk', type=int, required=True, help="Size of chunks of time dimension")
    parser.add_argument('-lat_chunk', '--latitude_chunk', type=int, required=True, help="Size of chunks of latitude dimension")
    parser.add_argument('-lon_chunk', '--longitude_chunk', type=int, required=True, help="Size of chunks of longitude dimension")
    args = parser.parse_args()

    unchunked_fmc = xr.open_dataset(fmc_stack_path.format(args.year))
    fmc_dates = unchunked_fmc.time.data
    print(fmc_dates)
    fmc_dates = [datetime.utcfromtimestamp(d.astype('O')/1e9) for d in fmc_dates]
    fmc_mean = unchunked_fmc.fmc_mean.data

    t_chunk = args.time_chunk
    lat_chunk = args.latitude_chunk
    lon_chunk = args.longitude_chunk

    dest = '{0}/fmc_{1}_chunked_t{2}_lat{3}_lon{4}_nocompress.nc'.format(args.destination, args.year, t_chunk, lat_chunk, lon_chunk)

    pack_fmc_mosaic_chunks(fmc_dates, fmc_mean, dest, t_chunk, lat_chunk, lon_chunk)
    del fmc_mean


