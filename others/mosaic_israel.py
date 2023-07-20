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
import os


#AUSTRIA

lat_max_of_int = 40.
lat_min_of_int = 30.

lon_max_of_int = 52.3
lon_min_of_int = 23.

res_of_int = 0.005


fmc_stack_path = '/g/data/ub8/au/FMC/israel/tiles/ISR_fmc_c6_{}_{}.nc'
_tiles = ['h20v05','h21v05']
wgs84_wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
tile_size = 2400


def pack_fmc_mosaic(date, fmc_median, fmc_stdv, q_mask, dest):
    lat_max = lat_max_of_int
    lat_min = lat_min_of_int
    lon_max = lon_max_of_int
    lon_min = lon_min_of_int
    res = res_of_int
    
    x_size = int((lon_max - lon_min)/res)
    y_size = int((lat_min - lat_max)/(-1*res))
    
    
    with netCDF4.Dataset(dest, 'w', format='NETCDF4_CLASSIC') as ds:
        with open('nc_metadata.json') as data_file:
            attrs = json.load(data_file)
            for key in attrs:
                setattr(ds, key, attrs[key])
        setattr(ds, "date_created", datetime.now().strftime("%Y%m%dT%H%M%S"))
        
        t_dim = ds.createDimension("time", 1)
        x_dim = ds.createDimension("longitude", fmc_median.shape[1])
        y_dim = ds.createDimension("latitude", fmc_median.shape[0])

        var = ds.createVariable("time", "f8", ("time",))
        var.units = "seconds since 1970-01-01 00:00:00.0"
        var.calendar = "standard"
        var.long_name = "Time, unix time-stamp"
        var.standard_name = "time"
        var[:] = netCDF4.date2num([date], units="seconds since 1970-01-01 00:00:00.0", calendar="standard")

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
        
        var = ds.createVariable("lfmc_median", 'f4', ("time", "latitude", "longitude"), fill_value=-9999.9)
        var.long_name = "Median Live Fuel Moisture Content"
        var.units = '%'
        var[:] = fmc_median[None,...]

        var = ds.createVariable("lfmc_stdv", 'f4', ("time", "latitude", "longitude"), fill_value=-9999.9)
        var.long_name = "Standard Deviation Live Fuel Moisture Content"
        var.units = '%'
        var[:] = fmc_stdv[None,...]
        
        var = ds.createVariable("quality_mask", 'i1', ("time", "latitude", "longitude"), fill_value=0)
        var.long_name = "Quality Mask"
        var.units = 'Cat'
        var[:] = q_mask[None,...]


def get_fmc(date, tile, var_name):
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)
    fmc_file = fmc_stack_path.format(d.year, tile)
    
    return xr.open_dataset(fmc_file)[var_name].loc[date, :].data

def get_mosaic_stack_dates(f_path):
    if os.path.isfile(f_path):
        ds = xr.open_dataset(f_path)
        return ds.time.data
        
    return []

def get_fmc_stack_dates(year):
    dates = []

    for _tile in _tiles:
        flam_file = fmc_stack_path.format(year, _tile)
        if not os.path.isfile(flam_file):
            print("Missing:", _tile)
            return []
        ds = xr.open_dataset(flam_file)
        if not dates:
            dates = list(ds.time.data)
        else:
            dates = [d for d in dates if d in list(ds.time.data)]
        
    return dates

def compose_mosaic(date, n_band, var_name, data_type):
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)

    lat_max = lat_max_of_int
    lat_min = lat_min_of_int
    lon_max = lon_max_of_int
    lon_min = lon_min_of_int
    res = res_of_int

    x_size = int((lon_max - lon_min)/res)
    y_size = int((lat_min - lat_max)/(-1*res))

    geot = [lon_min - res/2, res, 0., lat_max + res/2, 0., -1*res]  #gdal geotransform indicate top left corner, not the coord of centre of top left pixel
    
    src = gdal.GetDriverByName('MEM').Create('', tile_size, tile_size, 1, data_type,)

    dst = gdal.GetDriverByName('MEM').Create('', x_size, y_size, 1, data_type,)
    if data_type == gdal.GDT_Float32:
        dst.GetRasterBand(1).WriteArray(np.ones((y_size, x_size), dtype=np.float32) * -9999.9)
    dst.SetGeoTransform(geot)
    dst.SetProjection(wgs84_wkt)

    for _tile in _tiles:
        fname = fmc_stack_path.format(d.year, _tile)
        stack = gdal.Open('NETCDF:"{}":{}'.format(fname, var_name))
        if stack is None:
            continue
        
        band = stack.GetRasterBand(n_band).ReadAsArray()
        src.GetRasterBand(1).WriteArray(band)
    
        src.SetGeoTransform(stack.GetGeoTransform())
        src.SetProjection(stack.GetProjection())
        err = gdal.ReprojectImage(src, dst, None, None, gdal.GRA_NearestNeighbour)
    
    return dst.ReadAsArray()

def update_fmc_mosaic(date, n_band, dst, tmp, comp):
            
    fmc_median = compose_mosaic(date, n_band, "lfmc_median", gdal.GDT_Float32)
    fmc_stdv = compose_mosaic(date, n_band, "lfmc_stdv", gdal.GDT_Float32)
    q_mask = compose_mosaic(date, n_band, "quality_mask", gdal.GDT_Byte)
    
    tmp_file = os.path.join(tmp, uuid.uuid4().hex + ".nc")
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)
    pack_fmc_mosaic(d, fmc_median, fmc_stdv, q_mask, tmp_file)

    if not os.path.isfile(dst):
        shutil.move(tmp_file, dst)
    else:
        tmp_file2 = os.path.join(tmp, uuid.uuid4().hex + ".nc")
        os.system("cdo mergetime {} {} {}".format(tmp_file, dst, tmp_file2))
        os.remove(tmp_file)
        if comp:
            # In case the UNLIMITED time dimension is causing problems. nccopy has: 
            # [-u] convert unlimited dimensions to fixed size in output
            tmp_file3 = os.path.join(tmp, uuid.uuid4().hex + ".nc")
            os.system("nccopy -d 4 -c 'time/4,y/240,x/240' {} {}".format(tmp_file2, tmp_file3))
            os.remove(tmp_file2)
            shutil.move(tmp_file3, dst)
        else: 
            shutil.move(tmp_file2, dst)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Modis Vegetation Analysis argument parser""")
    parser.add_argument('-y', '--year', type=int, required=True, help="Year of data.")
    parser.add_argument('-c', '--compression', action='store_true', help="Apply compression to destination netCDF4.")
    parser.add_argument('-dst', '--destination', required=True, type=str, help="Full path to destination.")
    parser.add_argument('-tmp', '--tmp', required=True, type=str, help="Full path to destination.")
    args = parser.parse_args()

    fmc_dates = get_fmc_stack_dates(args.year)
    mosaic_dates = get_mosaic_stack_dates(args.destination)
    print(fmc_dates)
    print(mosaic_dates)

    for band, fmc_date in enumerate(fmc_dates):
        if fmc_date not in mosaic_dates:
            print(fmc_date)
            update_fmc_mosaic(fmc_date, band+1, args.destination, args.tmp, args.compression)

