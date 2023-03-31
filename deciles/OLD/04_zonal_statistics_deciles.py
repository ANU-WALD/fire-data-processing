import os
import sys
import time
import numpy as np
from copy import copy

import netCDF4 as nc
from netCDF4 import num2date

from functions_io import save_pickle

from multiprocessing import Pool
import warnings

"""
convert plg to raster with raster size and extent of flamability deciles

polygons:
/g/data1a/xc0/original/GIS/Australia/ABS/LGAs
used QGIS for rasterization

gdal_rasterize -l LGA11aAust_wgs84 -a LGA_CODE11 -tr 0.005 0.005 -a_nodata -9999.0 -te 112.9975 -43.9975 153.9975 -9.9975 -ot Float32 -of netCDF -co WRITE_BOTTOMUP=NO /g/data/xc0/user/ali/projects/AFMS/c6/mask_areas/LGA11aAust_wgs84.shp /g/data/xc0/user/ali/projects/AFMS/c6/mask_areas/mask_plgs.nc


sdd     single date decile and decile group file in NetCDF format

"""
# /g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_deciles.py /g/data/ub8/au/FMC/calc_deciles/data/temp flammability 2018 LGA

temp_path = sys.argv[1]
nc_var = sys.argv[2]
nc_year = sys.argv[3]
plg_name = sys.argv[4]  # LGA or FWA or States

# nc_var = 'flammability'
# nc_year = '2018'
# temp_path = '/g/data/ub8/au/FMC/calc_deciles/data/temp'
# plg_name = 'LGA'

var_short_dict = {
    'flammability': 'flam',
    'fmc_mean': 'fmc'
}
nc_var_short = var_short_dict[nc_var]

temp_path += '/' + nc_var_short

onc_file = nc_var_short + '_c6_' + nc_year + '.nc'
onc_path = '/g/data/ub8/au/FMC/c6/mosaics'  # file containing flam for all dates
onc_path_file = onc_path + '/' + onc_file

myd_path = temp_path

sdd_file = nc_var_short + '_c6_' + nc_year + '_dc.nc'
sdd_path = '/g/data/ub8/au/FMC/c6/mosaics/deciles'
sdd_temp_path = temp_path + '/sdd'

sdd_path_file = sdd_path + '/' + sdd_file
sdd_temp_path_file = sdd_temp_path + '/' + sdd_file

zst_temp_path = temp_path + '/zonal_stats'
zst_file = nc_var_short + '__' + plg_name + '__' + nc_year + '__dc_zonal_stat.pk'

zst_temp_path_file = zst_temp_path + '/' + zst_file

if not os.path.exists(zst_temp_path):
    os.mkdir(zst_temp_path)

if plg_name == 'LGA':
    nc_plg_path_file = '/g/data/ub8/au/FMC/calc_deciles/data/LGAs/LGA11aAust.nc'
elif plg_name == 'FWA':
    nc_plg_path_file = '/g/data/ub8/au/FMC/calc_deciles/data/FWA/gfe_fire_weather.nc'
else:
    nc_plg_path_file = '/g/data/ub8/au/FMC/calc_deciles/data/States/aus_states.nc'

# getting plg ids from the netcdf file
with nc.Dataset(nc_plg_path_file, 'r') as plgs_fid:
    plgs_arr = np.array(plgs_fid.variables['Band1'][:])
    plgs_arr[plgs_arr == -9999] = np.nan
    plg_ids = np.unique(plgs_arr[~np.isnan(plgs_arr)])

nc_vegmask_path_file = '/g/data/ub8/au/FMC/c6/mosaics/mask_2018.nc'
# getting veg mask layer the netcdf file
with nc.Dataset(nc_vegmask_path_file, 'r') as vegmask_fid:
    vegmask_arr = np.array(vegmask_fid.variables['quality_mask'][:]).astype(np.float)[0, :, :]
    # vegmask_arr[vegmask_arr == 0] = np.nan
    vegmask_ids = np.unique(vegmask_arr[~np.isnan(vegmask_arr)])


def get_nc_dates(nc_fid):
    time_vals = nc_fid.variables['time'][:]
    time_units = nc_fid.variables['time'].getncattr('units')
    time_calendar = 'gregorian'
    return num2date(time_vals, units=time_units, calendar=time_calendar).tolist()


zonal_stat_dict = {}
with nc.Dataset(sdd_temp_path_file, 'r') as sdd_fid:
    sdd_dates = get_nc_dates(nc_fid=sdd_fid)

    cnt_dt = -1
    for sdd_date in sdd_dates:
        cnt_dt += 1

        dc_vals = np.array(sdd_fid.variables['decile_values'][cnt_dt, :, :]).astype(np.float32)
        dc_vals[dc_vals == 111] = np.nan


        def process_date(plg_id_f):
            out_dict = {
                'plg_id': plg_id_f,
                'stats': {},
            }
            pg_arr = copy(plgs_arr)
            np_arr = copy(dc_vals)
            vg_arr = copy(vegmask_arr)

            pg_arr[pg_arr != plg_id_f] = np.nan
            pg_arr_count = np.count_nonzero(~np.isnan(pg_arr))

            np_arr[plgs_arr != plg_id_f] = np.nan
            np_arr_count = np.count_nonzero(~np.isnan(np_arr))

            np_cover = np.round((np_arr_count / pg_arr_count) * 100.0, 1)
            out_dict['stats']['coverage'] = np_cover

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)

                out_dict['stats']['min'] = np.nanmin(np_arr)
                out_dict['stats']['max'] = np.nanmax(np_arr)
                out_dict['stats']['avg'] = np.round(np.nanmean(np_arr), decimals=2)

                for vg_class in [0.0, 1.0, 2.0, 3.0]:
                    np_arr0 = copy(np_arr)
                    np_arr0[vg_arr != vg_class] = np.nan

                    vg_arr_count = np.count_nonzero(~np.isnan(np_arr0))
                    vg_cover = np.round((vg_arr_count / pg_arr_count) * 100.0, 1)
                    out_dict['stats']['coverage_' + str(int(vg_class))] = vg_cover

                    out_dict['stats']['min_' + str(int(vg_class))] = np.nanmin(np_arr0)
                    out_dict['stats']['max_' + str(int(vg_class))] = np.nanmax(np_arr0)
                    out_dict['stats']['avg_' + str(int(vg_class))] = np.round(np.nanmean(np_arr0), decimals=2)

            return out_dict


        st = time.time()
        p = Pool(processes=16)

        p_results = p.map(process_date, plg_ids)
        p.close()
        p.join()

        for item in p_results:
            plg_id = item['plg_id']
            plg_id_str = str(int(plg_id))
            if not plg_id_str in zonal_stat_dict:
                zonal_stat_dict[plg_id_str] = {}
            zonal_stat_dict[plg_id_str][sdd_date] = item['stats']
        print('this', sdd_date, 'time', time.time() - st, 'last', sdd_dates[-1])

    save_pickle(object=zonal_stat_dict, path_file=zst_temp_path_file)
