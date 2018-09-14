import os.path
import numpy as np
import argparse
from glob import glob
from utils import pack_data
from datetime import datetime
import xarray as xr
import uuid
import shutil
import sys

fmc_stack_path = "/g/data/fj4/scratch/2018/MCD43A4.A{}.{}.006.LFMC.nc"
tile_size = 2400

def flammability(fmc_t1, fmc_t2):
    return None

def get_fmc_stack_dates(f_path):
    if os.path.isfile(f_path):
        ds = xr.open_dataset(f_path)
        return ds.time.data
        
    return []

def get_flammability_stack_dates(f_path):
    if os.path.isfile(f_path):
        ds = xr.open_dataset(f_path)
        return ds.time.data
        
    return []

def update_flammability(src, dst, tmp, comp):
    
    date = datetime.strptime(modis_path.split("/")[-2], '%Y.%m.%d')
    tile_id = modis_tile.split("/")[-1].split(".")[2]

    veg_type = get_vegmask(tile_id, date)
    ref_stack, q_mask = get_reflectances(modis_path)
    mean, stdv = fmc(ref_stack, q_mask, veg_type)
    tmp_file = os.path.join(tmp, uuid.uuid4().hex + ".nc")

    pack_data(modis_path, date, mean, stdv, q_mask, tmp_file)

    if not os.path.isfile(dst):
        shutil.move(tmp_file, dst)
    else:
        tmp_file2 = os.path.join(tmp, uuid.uuid4().hex + ".nc")
        os.system("cdo mergetime {} {} {}".format(tmp_file, dst, tmp_file2))
        os.remove(tmp_file)
        if comp:
            print("compressing")
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
    parser.add_argument('-c', '--compression', action='store_true', help="Apply compression to destination netCDF4.")
    parser.add_argument('-dst', '--destination', required=True, type=str, help="Full path to destination.")
    parser.add_argument('-tmp', '--tmp', required=True, type=str, help="Full path to destination.")
    args = parser.parse_args()

    fmc_dates = get_fmc_stack_dates(fmc_stack_path.format(2018, "h30v11"))
    flam_dates = get_flammability_stack_dates(dst)

    for fmc_date in fmc_dates:
        if fmc_date not in flam_dates:
            print(fmc_date)
    
    sys.exit(0)

    update_flammability(t, args.destination, args.tmp, args.compression)
