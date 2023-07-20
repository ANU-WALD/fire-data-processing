import os.path
from osgeo import gdal
import numpy as np
import argparse
from glob import glob
from utils import get_top_n_functor, get_fmc_functor_median, pack_fmc, get_vegmask
from datetime import datetime
import xarray as xr
import uuid
import shutil
import sys

mcd43_root = '/g/data/ub8/au/FMC/intermediary_files/NSW_MCD43A4.061'
tile_size = 2400

def fmc(raster_stack, q_mask, veg_type, band_mask):
    ndvi_raster = (raster_stack[:, :, 1]-raster_stack[:, :, 0])/(raster_stack[:, :, 1]+raster_stack[:, :, 0])

    # In case the mask doesn't exist
    if q_mask is None:
        q_mask = np.ones((tile_size, tile_size), dtype=bool)

    median_arr = np.ones((tile_size, tile_size), dtype=np.float32) * -9999.9
    std_arr = np.ones((tile_size, tile_size), dtype=np.float32) * -9999.9
    
    get_top_n = get_top_n_functor()
    get_fmc = get_fmc_functor_median()
    
    for i in range(tile_size):
        for j in range(tile_size):
            #if veg_type[j, i] > 0 and ndvi_raster[j, i] > .15 and q_mask[j, i]: #OLD
            #if veg_type[j, i] > 0 and ndvi_raster[j, i] > .15:  #OLD
            if veg_type[j, i] > 0 and ndvi_raster[j, i] > .15 and band_mask[j, i]:
                top_40 = get_top_n(raster_stack[j, i, :], veg_type[j, i], 40)
                median_arr[j, i], std_arr[j, i] = get_fmc(top_40)

    return median_arr, std_arr


def get_reflectances(tile_path):
    #Special case where we don't use all the bands, only bands 1, 2, 4, 6, 7 are needed for the LUTs
    bands = [1,2,4,6,7]

    tile_file = xr.open_dataset(tile_path)

    # sometimes band 6 (maybe also other bands?) has more missing data than other bands, 
    # the following mask is to make sure the final LFMC images are composed only by pixels present in all bands, to avoid artifacts
    band_mask = ~np.isnan(tile_file.Nadir_Reflectance_Band1[:].data.astype(np.float32))

    ref_stack = tile_file.Nadir_Reflectance_Band1[:].data.astype(np.float32)
    q_mask = tile_file.BRDF_Albedo_Band_Mandatory_Quality_Band1[:].data
    
    for i in bands[1:]:
        ref_array = tile_file["Nadir_Reflectance_Band{}".format(i)][:].data.astype(np.float32)

        ref_stack = np.dstack((ref_stack, ref_array))
        q_mask = np.dstack((q_mask, tile_file["BRDF_Albedo_Band_Mandatory_Quality_Band{}".format(i)]))
        band_mask = np.dstack((band_mask, ~np.isnan(ref_array)))
    
    # NDII6 compositions between bands 2 and 6 -> indexes 1 and 3
    ref_stack = np.dstack((ref_stack, (ref_stack[:, :, 1]-ref_stack[:, :, 3])/(ref_stack[:, :, 1]+ref_stack[:, :, 3])))

    q_mask = q_mask == 0
    q_mask = np.all(q_mask, axis=2)

    band_mask = np.all(band_mask, axis=2)

    return ref_stack, q_mask, band_mask


def get_fmc_stack_dates(f_path):
    if os.path.isfile(f_path):
        ds = xr.open_dataset(f_path)
        return ds.time.data
        
    return []

def get_mcd43_paths(year, tile, file_dates):
    paths = []

    dirs = glob(mcd43_root + "/*")

    for tile_dir in dirs:
        tile_date = tile_dir.split("/")[-1]
        if len(tile_date.split(".")) != 3 or int(tile_date.split(".")[0]) != year:
            continue
        d = datetime.strptime(tile_date, '%Y.%m.%d')
        if np.datetime64(d) not in file_dates and d.year == year:
            files = glob(tile_dir + "/*.hdf")
            for f in files:
                f_parts = os.path.basename(f).split(".")
                if len(f_parts) == 6 and f_parts[2] == tile:
                    paths.append(f)

    return sorted(paths)


def update_fmc(modis_path, dst, tmp, comp):
    date = datetime.strptime(modis_path.split("/")[-2], '%Y.%m.%d')
    tile_id = modis_tile.split("/")[-1].split(".")[2]

    veg_type = get_vegmask(tile_id, date)
    ref_stack, q_mask, band_mask = get_reflectances(modis_path)
    median, stdv = fmc(ref_stack, q_mask, veg_type, band_mask)
    tmp_file = os.path.join(tmp, uuid.uuid4().hex + ".nc")

    pack_fmc(modis_path, date, median, stdv, q_mask, tmp_file)

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
    parser.add_argument('-d', '--date', type=str, required=True, help="Date with format YYYYMMDD or YYYY to update with latest data.")
    parser.add_argument('-c', '--compression', action='store_true', help="Apply compression to destination netCDF4.")
    parser.add_argument('-dst', '--destination', required=True, type=str, help="Full path to destination.")
    parser.add_argument('-tmp', '--tmp', required=True, type=str, help="Full path to destination.")
    args = parser.parse_args()

    file_dates = get_fmc_stack_dates(args.destination)
    modis_tiles = []
    if len(args.date) == 8:
        d = datetime.strptime(args.date, "%Y%m%d")
        if file_dates is not None and np.datetime64(d) in file_dates:
            print("Time layer already exists in destination file.")
            sys.exit(0)
        modis_glob = "{}/{}/MCD43A4.A{}{:03d}.{}.061.*.hdf".format(mcd43_root, d.strftime("%Y.%m.%d"), d.year, d.timetuple().tm_yday, args.tile)
        modis_tiles = glob(modis_glob)
        if len(modis_tiles) != 1:
            sys.exit(1)
    elif len(args.date) == 4:
        modis_tiles = get_mcd43_paths(int(args.date), args.tile, file_dates)
    else:
        sys.exit(1)

    for modis_tile in modis_tiles:
        print(modis_tile)
        update_fmc(modis_tile, args.destination, args.tmp, args.compression)
