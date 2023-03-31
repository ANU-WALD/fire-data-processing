import os
import glob
import sys
import numpy as np
import netCDF4 as nc
from functions_io import save_pickle, load_pickle
from function_calc_decile_concurrent import calc_dec_concurrent
from functions_nc import copy_nc_exclude

"""
1- tile nc file to small (100x100) tiles and save them in a temp folder
2- calculate deciles in multiprocessing mode as save in temp
3- merge decile files to make a mosaic and save
4- convert mosaic to nc format

WARNING:
DO NOT RUN THIS SCRIPT IN PARALLEL
SETP 3 NEEDS LARGE MEMORY

"""
# /g/data/xc0/software/python/miniconda3/bin/python3 02_calc_multiyear_deciles.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp fmc_mean 1 tiling

temp_path = sys.argv[1]
nc_var = sys.argv[2]
nc_month = sys.argv[3]
step = sys.argv[4]

# step = 'tiling' # tiling or merging
# nc_var = 'flammability'
# nc_month = '7'
# temp_path = '/g/data/xc0/project/FMC_Australia/calc_deciles/data/temp'

var_short_dict = {
    'flammability': 'flam',
    'fmc_mean': 'fmc'
}
nc_var_short = var_short_dict[nc_var]

temp_path += '/' + nc_var_short

nc_in_file = nc_var_short + '_' + nc_month + '.nc'
nc_dc_file = nc_var_short + '_' + nc_month + '_dc.nc'

temp_tile_path = temp_path + '/temp_tiles'

if not os.path.exists(temp_tile_path):
    os.mkdir(temp_tile_path)

nc_in_path_file = temp_path + '/' + nc_in_file
nc_dc_path_file = temp_path + '/' + nc_dc_file

tile_path = temp_tile_path + '/' + nc_in_file
if not os.path.exists(tile_path):
    os.mkdir(tile_path)

tile_dc_merge_path = tile_path + '/' + 'deciles_merge'
if not os.path.exists(tile_dc_merge_path):
    os.mkdir(tile_dc_merge_path)

nc_fid = nc.Dataset(nc_in_path_file, 'r')
dim_t, dim_y, dim_x = nc_fid.variables[nc_var].shape
nc_fid.close()

if step == 'tiling':
    """ STEP 1: Tiling"""
    with nc.Dataset(nc_in_path_file, 'r') as nc_fid:
        st_x, st_y = 0, 0
        cnt = 0
        tile_size = 100

        for y_i in range(tile_size, dim_y + 1, tile_size):

            if y_i < dim_y - tile_size:
                en_y = y_i
            else:
                en_y = dim_y

            for x_i in range(tile_size, dim_x + 1, tile_size):

                if x_i < dim_x - tile_size:
                    en_x = x_i
                else:
                    en_x = dim_x

                print(st_y, en_y, '|', st_x, en_x)
                cnt += 1
                tile_path_file = tile_path + '/' + nc_var + '__' + str(cnt) + '.pk'
                if not os.path.exists(tile_path_file):
                    nc_data = np.array(nc_fid.variables[nc_var][:, st_y:en_y, st_x:en_x])
                    nc_data[nc_data == -9999.9] = np.nan

                    tile_dict = {
                        'st_y': st_y,
                        'en_y': en_y,
                        'st_x': st_x,
                        'en_x': en_x,
                        'data': nc_data
                    }

                    save_pickle(tile_dict, tile_path_file)
                st_x = x_i
            st_x = 0
            st_y = y_i

    """ Calculate deciles concurrently """
    tile_path_files = sorted(glob.glob(tile_path + '/*.pk'))
    print('total number of tiles', len(tile_path_files))
    calc_dec_concurrent(tile_path_files=tile_path_files)


if step == 'merging':
    """ STEP 2: merge and export to nc """

    d_arr = np.empty((9, dim_y, dim_x))
    d_arr[:] = np.nan

    tile_dc_path = tile_path + '/' + 'deciles'
    tile_dc_path_files = glob.glob(tile_dc_path + '/*_dc.pk')

    for tile_dc_path_file in tile_dc_path_files:

        tile_dc_dict = load_pickle(tile_dc_path_file)
        st_y = tile_dc_dict['st_y']
        en_y = tile_dc_dict['en_y']
        st_x = tile_dc_dict['st_x']
        en_x = tile_dc_dict['en_x']
        print(tile_dc_path_file, st_y, en_y, st_x, en_x)
        cnt_q = 0
        for q in range(10, 100, 10):
            d_arr[cnt_q, st_y:en_y, st_x:en_x] = tile_dc_dict['deciles'][q]
            cnt_q += 1

    tile_dc_merge_path_file = tile_dc_merge_path + '/' + 'tiles_merge.pk'
    if os.path.exists(tile_dc_merge_path_file):
        os.remove(tile_dc_merge_path_file)

    save_pickle(d_arr, tile_dc_merge_path_file)
    d_arr = load_pickle(tile_dc_merge_path_file)
    if nc_var == 'flammability':
        d_arr[d_arr < 0.0] = -9999.9
        d_arr[d_arr > 1.0] = -9999.9

    d_arr[np.isnan(d_arr)] = -9999.9

    if os.path.exists(nc_dc_path_file):
        os.remove(nc_dc_path_file)

    copy_nc_exclude(src_path_file=nc_in_path_file, dst_path_file=nc_dc_path_file,
                    exclude_dims=['time'],
                    exclude_vars=['time', nc_var])

    with nc.Dataset(nc_dc_path_file, "r+", format='NETCDF4_CLASSIC') as dst:
        dim = dst.createDimension('percentile', 9)
        var = dst.createVariable('percentile', np.int32, ('percentile',))
        var.long_name = 'percentile'
        var.units = '%'
        var[:] = np.linspace(10, 90, 9).astype(np.int32)

        var = dst.createVariable(nc_var + '_deciles', 'f4', ('percentile', 'latitude', 'longitude'), fill_value=-9999.9)
        var.long_name = nc_var + ' deciles'
        var.units = '%'
        var.grid_mapping = 'crs'

        var[:] = d_arr
