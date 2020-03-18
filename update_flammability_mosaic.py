import os.path
import numpy as np
import argparse
from glob import glob
from utils import pack_flammability_mosaic
from datetime import datetime, timedelta
import xarray as xr
import uuid
import shutil
import sys
from osgeo import gdal 

flam_stack_path = "/g/data/ub8/au/FMC/c6/flam_c6_{}_{}.nc"
fmc_stack_path = "/g/data/ub8/au/FMC/c6/fmc_c6_{}_{}.nc"
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

def compose_mosaic(date, n_band, var_name, data_type):
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
    
    src = gdal.GetDriverByName('MEM').Create('', tile_size, tile_size, 1, data_type,)

    geot = [lon0, res, 0., lat0, 0., -1*res]
    dst = gdal.GetDriverByName('MEM').Create('', x_size, y_size, 1, data_type,)
    if data_type == gdal.GDT_Float32:
        dst.GetRasterBand(1).WriteArray(np.ones((y_size, x_size), dtype=np.float32) * -9999.9)
    dst.SetGeoTransform(geot)
    dst.SetProjection(wgs84_wkt)

    for au_tile in au_tiles:
        fname = flam_stack_path.format(d.year, au_tile)
        stack = gdal.Open('NETCDF:"{}":{}'.format(fname, var_name))
        if stack is None:
            continue
        
        band = stack.GetRasterBand(n_band).ReadAsArray()
        src.GetRasterBand(1).WriteArray(band)
    
        src.SetGeoTransform(stack.GetGeoTransform())
        src.SetProjection(stack.GetProjection())
        err = gdal.ReprojectImage(src, dst, None, None, gdal.GRA_NearestNeighbour)
    
    return dst.ReadAsArray()

def update_flammability_mosaic(date, n_band, dst, tmp, comp):
            
    flam = compose_mosaic(date, n_band, "flammability", gdal.GDT_Float32)
    qmask = compose_mosaic(date, n_band, "quality_mask", gdal.GDT_Byte)
    
    tmp_file = os.path.join(tmp, uuid.uuid4().hex + ".nc")
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)
    pack_flammability_mosaic(d, flam, qmask, tmp_file)

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

    flam_dates = get_flammability_stack_dates(args.year)
    mosaic_dates = get_mosaic_stack_dates(args.destination)
    print(flam_dates)
    print(mosaic_dates)

    for band, flam_date in enumerate(flam_dates):
        if flam_date not in mosaic_dates:
            print(flam_date)
            update_flammability_mosaic(flam_date, band+1, args.destination, args.tmp, args.compression)

