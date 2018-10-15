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

fmc_stack_path = "/g/data/fj4/scratch/fmc_c6_{}_{}.nc"
fmc_mean_path = "/g/data/fj4/scratch/mean_2001_2016_{}.nc"
tile_size = 2400

def flammability(fmc_t1, fmc_t2):
    return None


def get_fmc_stack_dates(year, tile_id):
    dates = np.array([], dtype=np.datetime64)
    
    fmc_file = fmc_stack_path.format(year-1, tile_id)
    if os.path.isfile(fmc_file):
        print("The source FMC file for the previous year exists.")
        ds = xr.open_dataset(fmc_file)
        dates = np.append(dates, ds.time.data)
    
    fmc_file = fmc_stack_path.format(year, tile_id)
    if os.path.isfile(fmc_file):
        print("The source FMC file for the current year exists.")
        ds = xr.open_dataset(fmc_file)
        dates = np.append(dates, ds.time.data)

    return dates

def get_fmc(date, tile):
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)
    fmc_file = fmc_stack_path.format(d.year, tile)
    
    if os.path.isfile(fmc_file):
        return xr.open_dataset(fmc_file).lfmc_mean.loc[date, :].data

    return None

def get_qmask(date, tile):
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)
    fmc_file = fmc_stack_path.format(d.year, tile)
    
    return xr.open_dataset(fmc_file).quality_mask.loc[date, :].data

def get_flammability_stack_dates(f_path):
    if os.path.isfile(f_path):
        ds = xr.open_dataset(f_path)
        return ds.time.data
        
    return []

def get_t(date, tile):
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)
    fmc_file = fmc_stack_path.format(d.year, tile)
    if os.path.isfile(fmc_file):
        t_dim = xr.open_dataset(fmc_file).time.data
        idx = (np.abs(t_dim - date)).argmin()
        return t_dim[idx]

    return None

def compute_flammability(t, tile):
    #t = datetime.utcfromtimestamp(date.astype('O')/1e9)
    t1 = get_t(np.datetime64(t - timedelta(days=8), "ns"), tile)
    if t1 == None:
        return None, None
    t2 = get_t(np.datetime64(t - timedelta(days=16), "ns"), tile)
    if t2 == None:
        return None, None
    
    mean = xr.open_dataset(fmc_mean_path.format(tile)).lfmc_mean.data
    fmc_t1 = get_fmc(t1, tile)
    fmc_t2 = get_fmc(t2, tile)
    anomaly = fmc_t1 - mean
    diff = fmc_t2 - fmc_t1
 
    grass = 0.18 - 0.01 * mean + 0.020 * diff - 0.02 * anomaly
    grass = 1 / (1 + np.e ** - grass)
    shrub = 5.66 - 0.09 * mean + 0.005 * diff - 0.28 * anomaly
    shrub = 1 / (1 + np.e ** - shrub)
    forst = 1.51 - 0.03 * mean + 0.020 * diff - 0.02 * anomaly
    forst = 1 / (1 + np.e ** - forst)

    flammability = np.ones((tile_size*tile_size), dtype=np.float32) * -9999.9

    # 1=Grass, 2=Shrub, 3=Forest
    vegmask = get_vegmask(tile, t).flatten()
    flammability[vegmask==1] = grass.flatten()[vegmask==1]
    flammability[vegmask==2] = shrub.flatten()[vegmask==2]
    flammability[vegmask==3] = forst.flatten()[vegmask==3]

    return flammability.reshape((tile_size,tile_size)), anomaly

def update_flammability(date, tile_id, fmc_file, dst, tmp, comp):
            
    t1 = get_t(np.datetime64(date - timedelta(days=8), "ns"), tile_id)
    qmask = get_qmask(t1, tile_id)
    flam, anom = compute_flammability(date, tile_id)

    tmp_file = os.path.join(tmp, uuid.uuid4().hex + ".nc")
    pack_flammability(fmc_file, date, flam, anom, qmask, tmp_file)

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
    parser.add_argument('-t', '--tile', type=str, required=True, help="Modis tile in hXXvXX format.")
    parser.add_argument('-y', '--year', type=int, required=True, help="Year of data.")
    parser.add_argument('-c', '--compression', action='store_true', help="Apply compression to destination netCDF4.")
    parser.add_argument('-dst', '--destination', required=True, type=str, help="Full path to destination.")
    parser.add_argument('-tmp', '--tmp', required=True, type=str, help="Full path to destination.")
    args = parser.parse_args()

    fmc_file = fmc_stack_path.format(args.year, args.tile)
    fmc_dates = get_fmc_stack_dates(args.year, args.tile)
    flam_dates = [datetime.utcfromtimestamp(flam_date.astype('O')/1e9) for flam_date in get_flammability_stack_dates(args.destination)]

    for fmc_date in fmc_dates:
        d = datetime.utcfromtimestamp(fmc_date.astype('O')/1e9) + timedelta(days=8)
        if d.year == args.year and d not in flam_dates:
            print(datetime.utcfromtimestamp(fmc_date.astype('O')/1e9), d)
            update_flammability(d , args.tile, fmc_file, args.destination, args.tmp, args.compression)
