import os.path
from osgeo import gdal
import numpy as np
import argparse
from glob import glob
from utils import get_top_n_functor, get_fmc_functor, pack_data
from datetime import datetime
import xarray as xr
import uuid
import shutil
import sys

mcd43_root = "/g/data/u39/public/data/modis/lpdaac-tiles-c6/MCD43A4.006"
#modis_path = "/g/data/u39/public/data/modis/lpdaac-tiles-c6/MCD43A4.006/{}/MCD43A4.A{}{}.{}.006.*.hdf"
mcd12q1_path = "/g/data/u39/public/data/modis/lpdaac-tiles-c5/MCD12Q1.051"
tile_size = 2400

def fmc(raster_stack, q_mask, veg_type):
    ndvi_raster = (raster_stack[:, :, 1]-raster_stack[:, :, 0])/(raster_stack[:, :, 1]+raster_stack[:, :, 0])

    # In case the mask doesn't exist
    if q_mask is None:
        q_mask = np.ones((tile_size, tile_size), dtype=bool)

    mean_arr = np.zeros((tile_size, tile_size), dtype=np.float32)
    std_arr = np.zeros((tile_size, tile_size), dtype=np.float32)
    
    get_top_n = get_top_n_functor()
    get_fmc = get_fmc_functor()
    
    for i in range(tile_size):
        for j in range(tile_size):
            #if veg_type[j, i] > 0 and ndvi_raster[j, i] > .15 and q_mask[j, i]:
            if veg_type[j, i] > 0 and ndvi_raster[j, i] > .15:
                top_40 = get_top_n(raster_stack[j, i, :], veg_type[j, i], 40)
                mean_arr[j, i], std_arr[j, i] = get_fmc(top_40)

    return mean_arr, std_arr


def get_vegmask(tile_id, tile_date):
    dates = sorted(glob("{}/*".format(mcd12q1_path)))[::-1]

    for d in dates:
        msk_date =  datetime.strptime(d.split("/")[-1], '%Y.%m.%d')
        if msk_date > tile_date:
            continue
           
        files = glob("{0}/MCD12Q1.A{1}{2:03d}.{3}.051.*.hdf".format(d, msk_date.year, msk_date.timetuple().tm_yday, tile_id))
        if len(files) == 1:
            veg_mask = xr.open_dataset(files[0]).Land_Cover_Type_1[:].data

            veg_mask[veg_mask == 1] = 3
            veg_mask[veg_mask == 2] = 3
            veg_mask[veg_mask == 3] = 3
            veg_mask[veg_mask == 4] = 3
            veg_mask[veg_mask == 5] = 3
            veg_mask[veg_mask == 6] = 2
            veg_mask[veg_mask == 7] = 2
            veg_mask[veg_mask == 8] = 3
            veg_mask[veg_mask == 9] = 3
            veg_mask[veg_mask == 10] = 1
            veg_mask[veg_mask == 11] = 0
            veg_mask[veg_mask == 12] = 1
            veg_mask[veg_mask == 13] = 0
            veg_mask[veg_mask == 14] = 0
            veg_mask[veg_mask == 15] = 0
            veg_mask[veg_mask == 16] = 0
            veg_mask[veg_mask == 254] = 0
            veg_mask[veg_mask == 255] = 0
            
            return veg_mask
    
    return None


def get_reflectances(tile_path):
    #Special case where we don't use all the bands 1, 2, 4, 6, 7
    bands = [1,2,4,6,7]

    ref_stack = xr.open_dataset(tile_path).Nadir_Reflectance_Band1[:].data.astype(np.float32)
    q_mask = xr.open_dataset(tile_path).BRDF_Albedo_Band_Mandatory_Quality_Band1[:].data
    
    for i in bands[1:]:
        ref_stack = np.dstack((ref_stack, xr.open_dataset(tile_path)["Nadir_Reflectance_Band{}".format(i)][:].data.astype(np.float32)))
        q_mask = np.dstack((q_mask, xr.open_dataset(tile_path)["BRDF_Albedo_Band_Mandatory_Quality_Band{}".format(i)]))
    
    # VDII compositions between bands 2 and 6 -> indexes 1 and 3
    ref_stack = np.dstack((ref_stack, (ref_stack[:, :, 1]-ref_stack[:, :, 3])/(ref_stack[:, :, 1]+ref_stack[:, :, 3])))

    q_mask = q_mask == 0
    q_mask = np.all(q_mask, axis=2)

    return ref_stack, q_mask


def get_fmc_stack_dates(f_path):
    if os.path.isfile(f_path):
        ds = xr.open_dataset(f_path)
        return ds.time.data
        
    return None

def get_mcd43_dates(year, tile):
    paths = []
    for root, dirs, files in os.walk(mcd43_root):
        tile_dir = root.split("/")[-1]
        date_parts = tile_dir.split(".")
        if len(date_parts) != 3:
            continue
        y = int(date_parts[0])
        if y == year:
            for f in files:
                f_parts = f.split(".")
                if f.endswith(".hdf") and len(f_parts) == 6 and f_parts[2] == tile:
                    paths.append(datetime.strptime(tile_dir, "%Y.%m.%d"))

    return np.sort(np.array(paths, dtype=np.datetime64))


def update_fmc(modis_path, dst):

    date = datetime.strptime(modis_path.split("/")[-2], '%Y.%m.%d')
    tile_id = modis_tile.split("/")[-1].split(".")[2]

    veg_type = get_vegmask(tile_id, date)
    ref_stack, q_mask = get_reflectances(modis_path)
    mean, stdv = fmc(ref_stack, q_mask, veg_type)
    tmp_file = uuid.uuid4().hex + ".nc"

    pack_data(modis_path, date, mean, stdv, q_mask, tmp_file)

    if not os.path.isfile(dst):
        os.system("cdo mergetime {} {}".format(tmp_file, dst))
    else:
        tmp_file2 = uuid.uuid4().hex + ".nc"
        os.system("cdo mergetime {} {} {}".format(tmp_file, dst, tmp_file2))
        shutil.move(tmp_file2, dst)
    os.remove(tmp_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Modis Vegetation Analysis argument parser""")
    parser.add_argument('-t', '--tile', type=str, required=True, help="Modis tile in hXXvXX format.")
    parser.add_argument('-d', '--date', type=str, required=True, help="Date with format YYYYMMDD or YYYY to update with latest data.")
    parser.add_argument('-dst', '--destination', required=True, type=str, help="Full path to destination.")
    args = parser.parse_args()

    comp_dates = get_fmc_stack_dates(args.destination)

    modis_tiles = []
    if len(args.date) == 8:
        d = datetime.strptime(args.date, "%Y%m%d")
        if np.datetime64(d) in comp_dates:
            print("Time layer already exists in destination file.")
            sys.exit(0)

        modis_glob = "{}/{}/MCD43A4.A{}{}.{}.006.*.hdf".format(mcd43_root, d.strftime("%Y.%m.%d"), d.year, d.timetuple().tm_yday, args.tile)
        modis_tiles = glob(modis_glob)

        if len(modis_tiles) != 1:
            sys.exit(1)

    elif len(args.date) == 4:
        mcd_dates = get_mcd43_dates(int(args.date), args.tile, comp_tiles)
        print(mcd_dates)
        sys.exit(1)
    else:
        sys.exit(1)

    for modis_tile in modis_tiles:
        update_fmc(modis_tile, args.destination)
