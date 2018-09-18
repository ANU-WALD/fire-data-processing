import os.path
import numpy as np
import argparse
from glob import glob
from utils import pack_flammability, get_vegmask
from datetime import datetime, timedelta
import xarray as xr
import uuid
import shutil
import sys
from osgeo import gdal 
from matplotlib import pyplot as plt

flam_stack_path = "/g/data/fj4/scratch/{}_{}_flammability.nc"
fmc_stack_path = "/g/data/fj4/scratch/2018/MCD43A4.A{}.{}.006.LFMC.nc"
fmc_mean_path = "/g/data/ub8/au/FMC/mean_LVMC_{}.nc"
au_tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11"]
wgs84_wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
tile_size = 2400

def get_flammability(date, tile):
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)
    flam_file = flam_stack_path.format(d.year, tile)
    
    return xr.open_dataset(flam_file).lfmc_mean.loc[date, :].data

def get_mosaic_stack_dates(f_path):
    if os.path.isfile(f_path):
        ds = xr.open_dataset(f_path)
        return ds.time.data
        
    return []

def get_flammability_stack_dates(year):
    dates = []

    for au_tile in au_tiles:
        flam_file = flam_stack_path.format(year, au_tile)
        if not os.path.isfile(flam_file):
            print("Missing:", au_tile)
            return []
        ds = xr.open_dataset(flam_file)
        if not dates:
            dates = list(ds.time.data)
        else:
            dates = [d for d in dates if d in list(ds.time.data)]
        
    return dates

def compose_mosaic(date):
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)
    lat0 = -10.
    lat1 = -44.
    lon0 = 113.
    lon1 = 154.
    res = 0.005

    x_size = int((lon1 - lon0)/res)
    y_size = int((lat1 - lat0)/(-1*res))
    lats = np.linspace(lat0, lat1+res, num=y_size)
    lons = np.linspace(lon0, lon1-res, num=x_size)
    
    src = gdal.GetDriverByName('MEM').Create('', tile_size, tile_size, 1, gdal.GDT_Float32,)

    geot = [lon0, res, 0., lat0, 0., -1*res]
    dst = gdal.GetDriverByName('MEM').Create('', x_size, y_size, 1, gdal.GDT_Float32,)
    dst.SetGeoTransform(geot)
    dst.SetProjection(wgs84_wkt)

    for au_tile in au_tiles:
        print(au_tile)
        stack = gdal.Open('NETCDF:"/g/data/fj4/scratch/{}_{}_flammability.nc":flammability'.format(d.year, au_tile))
        if stack is None:
            print("mmmm", d.year, au_tile)
            continue
        
        band = stack.GetRasterBand(10).ReadAsArray()
        print(band.min(), band.max(), band.mean(), stack.GetGeoTransform())
        src.GetRasterBand(1).WriteArray(band)
    
        src.SetGeoTransform(stack.GetGeoTransform())
        src.SetProjection(stack.GetProjection())
        err = gdal.ReprojectImage(src, dst, None, None, gdal.GRA_NearestNeighbour)
        print(err)
    
    return dst.ReadAsArray()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Modis Vegetation Analysis argument parser""")
    parser.add_argument('-y', '--year', type=int, required=True, help="Year of data.")
    parser.add_argument('-c', '--compression', action='store_true', help="Apply compression to destination netCDF4.")
    parser.add_argument('-dst', '--destination', required=True, type=str, help="Full path to destination.")
    parser.add_argument('-tmp', '--tmp', required=True, type=str, help="Full path to destination.")
    args = parser.parse_args()

    flam_dates = get_flammability_stack_dates(args.year)
    mosaic_dates = get_mosaic_stack_dates(args.destination)
    print(flam_dates)
    print(mosaic_dates)

    for flam_date in flam_dates:
        if flam_date not in mosaic_dates:
            print(flam_date)
            plt.imsave("out_{}.png".format(flam_date), compose_mosaic(flam_date))
            #update_flammability(fmc_date, tile_id, fmc_file, args.destination, args.tmp, args.compression)
