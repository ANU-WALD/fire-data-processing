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

fmc_stack_path = "/g/data/fj4/scratch/2018/MCD43A4.A{}.{}.006.LFMC.nc"
fmc_mean_path = "/g/data/ub8/au/FMC/mean_LVMC_{}.nc"
tile_size = 2400

def flammability(fmc_t1, fmc_t2):
    return None


def get_fmc_stack_dates(f_path):
    if os.path.isfile(f_path):
        ds = xr.open_dataset(f_path)
        return ds.time.data
        
    return []


def get_fmc(date, tile):
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)
    #d = date.astype(datetime)
    fmc_file = fmc_stack_path.format(d.year, tile)
    
    return xr.open_dataset(fmc_file).lfmc_mean.loc[date, :].data


def get_flammability_stack_dates(f_path):
    if os.path.isfile(f_path):
        ds = xr.open_dataset(f_path)
        return ds.time.data
        
    return []

def get_t(date, tile):
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)
    fmc_file = fmc_stack_path.format(d.year, tile)
    t_dim = xr.open_dataset(fmc_file).time.data
    idx = (np.abs(t_dim - date)).argmin()
    return t_dim[idx]

def compute_flammability(date, tile):
    fmc_t = get_fmc(date, tile)
    t = datetime.utcfromtimestamp(date.astype('O')/1e9)
    t1 = get_t(np.datetime64(t - timedelta(days=8), "ns"), tile)
    t2 = get_t(np.datetime64(t - timedelta(days=16), "ns"), tile)
    
    mean = xr.open_dataset(fmc_mean_path.format(tile)).lvmc_mean.data
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
            
    flam, anom = compute_flammability(date, tile_id)
    
    tmp_file = os.path.join(tmp, uuid.uuid4().hex + ".nc")
    d = datetime.utcfromtimestamp(date.astype('O')/1e9)
    pack_flammability(fmc_file, d, flam, anom, tmp_file)

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
    if not os.path.isfile(fmc_file):
        print("The source FMC file does not exist.")
        sys.exit(0)

    fmc_dates = get_fmc_stack_dates(fmc_file)
    flam_dates = get_flammability_stack_dates(args.destination)
    print(fmc_dates)
    print(flam_dates)

    for fmc_date in fmc_dates:
        if fmc_date not in flam_dates:
            print(fmc_date)
            update_flammability(fmc_date, args.tile, fmc_file, args.destination, args.tmp, args.compression)
