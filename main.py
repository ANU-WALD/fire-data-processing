import os.path
from osgeo import gdal
import numpy as np
import argparse
from glob import glob
from utils import get_top_n_functor, get_fmc_functor
from datetime import datetime
import xarray as xr

mcd43a4_path = "/g/data/u39/public/data/modis/lpdaac-tiles-c6/MCD43A4.006"
mcd12q1_path = "/g/data/u39/public/data/modis/lpdaac-tiles-c5/MCD12Q1.051"
tile_size = 2400

def get_fmc(raster_stack, q_mask, veg_type):
    ndvi_raster = (raster_stack[:, :, 1]-raster_stack[:, :, 0])/(raster_stack[:, :, 1]+raster_stack[:, :, 0])

    print(ndvi_raster[:, 1], veg_type[:, 1])
    # In case the mask doesn't exist
    if q_mask is None:
        q_mask = np.ones((tile_size, tile_size), dtype=bool)

    mean_arr = np.zeros((tile_size, tile_size), dtype=np.float32)
    std_arr = np.zeros((tile_size, tile_size), dtype=np.float32)
    
    get_top_n = get_top_n_functor()
    get_fmc = get_fmc_functor()
    
    for i in range(tile_size):
        for j in range(tile_size):
            if veg_type[j, i] > 0 and ndvi_raster[j, i] > .15 and q_mask[j, i]:
                top_40 = get_top_n(raster_stack[j, i, :], veg_type[j, i], 40)
                mean_arr[j, i], std_arr[j, i] = get_fmc(top_40)

    return mean_arr, std_arr


def get_vegmask(h, v, tile_date):
    dates = sorted(glob("{}/*".format(mcd12q1_path)))[::-1]
    print(dates)
    for d in dates:
        msk_date =  datetime.strptime(d.split("/")[-1], '%Y.%m.%d')
        print(msk_date)
        if msk_date > tile_date:
            continue
           
        files = glob("{0}/MCD12Q1.A{1}{2:03d}.h{3:02d}v{4:02d}.051.*.hdf".format(d, msk_date.year, msk_date.timetuple().tm_yday, h, v))
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Modis Vegetation Analysis argument parser""")
    parser.add_argument(dest="modis_tile", type=str, help="Full path to a modis tile (HDF-EOS).")
    parser.add_argument(dest="destination", type=str, help="Full path to destination.")
    args = parser.parse_args()

    modis_tile = args.modis_tile
    destination = args.destination
    
    im_date =  datetime.strptime(modis_tile.split("/")[-2], '%Y.%m.%d')
    fname_parts = modis_tile.split("/")[-1].split(".")
    h = int(fname_parts[2][1:3])
    v = int(fname_parts[2][4:6])
    
    veg_type = get_vegmask(h, v, im_date)
    print("A")

    ref_stack, q_mask = get_reflectances(modis_tile)
    
    mean, std = get_fmc(ref_stack, q_mask, veg_type)

    #pack_data(modis_tile, mean, stdv, destination)
