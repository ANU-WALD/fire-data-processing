import os
import shutil
import sys
from netCDF4 import num2date, date2num
import netCDF4 as nc
import numpy as np
from copy import copy

from functions_nc import copy_nc_include


"""
For a given fire product, calculates the decile layer of each date based on the multi-year decile product.

onc     original netcdf (fire) file that we want to calculate decile for each date of it 
myd     multi-year decile product that we use for calculating sdd by comparing to it, in NetCDF format
sdd     single date decile and decile group file in NetCDF format

"""

""" INPUTS """
# /g/data/xc0/software/python/miniconda3/bin/python3 03_calc_single_year_deciles.py flammability /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp 2018

nc_var = sys.argv[1]
temp_path = sys.argv[2]
nc_year = sys.argv[3]


# nc_var = 'flammability'
# nc_year = '2018'
# temp_path = '/g/data/xc0/project/FMC_Australia/calc_deciles/data/temp'

var_short_dict = {
    'flammability': 'flam',
    'fmc_mean': 'fmc'
}
nc_var_short = var_short_dict[nc_var]

temp_path += '/' + nc_var_short

onc_path_file = '/g/data/ub8/au/FMC/c6/mosaics/' + nc_var_short + '_c6_' + nc_year + '.nc'
sdd_file = nc_var_short + '_c6_' + nc_year + '_dc.nc'
sdd_path = '/g/data/ub8/au/FMC/c6/mosaics/deciles'

# /g/data/ub8/au/FMC/c6/mosaics/deciles

myd_path = temp_path

sdd_temp_path = temp_path + '/sdd'

sdd_path_file = sdd_path + '/' + sdd_file
sdd_temp_path_file = sdd_temp_path + '/' + sdd_file

if not os.path.exists(sdd_temp_path):
    os.makedirs(sdd_temp_path, exist_ok=True)
print(sdd_path_file)

sdd_exist = False
if os.path.exists(sdd_path_file):
    shutil.copyfile(sdd_path_file, sdd_temp_path_file)
    sdd_exist = True
else:
    copy_nc_include(src_path_file=onc_path_file, dst_path_file=sdd_temp_path_file,
                    include_dims=['time', 'longitude', 'latitude'],
                    include_vars=['longitude', 'latitude'])

with nc.Dataset(sdd_temp_path_file, "r+", format='NETCDF4_CLASSIC') as sdd_fid:
    if not sdd_exist:
        var_sdd_d = sdd_fid.createVariable('decile_values', np.int8, ('time', 'latitude', 'longitude'), fill_value=111)
        var_sdd_d.long_name = 'deciles'
        var_sdd_d.units = 'int8'

        var_sdd_g = sdd_fid.createVariable('decile_groups', np.int8, ('time', 'latitude', 'longitude'), fill_value=111)
        var_sdd_g.long_name = 'decile groups'
        var_sdd_g.units = 'int8'

        var_sdd_time = sdd_fid.createVariable('time', 'float32', ('time'))
        var_sdd_time.standard_name = 'time'
        var_sdd_time.long_name = 'Time, unix time-stamp'

        var_sdd_time.units = 'seconds since 1970-01-01 00:00:00.0'
        var_sdd_time.calendar = 'standard'

        sdd_date_list = []
    else:
        # to check this part
        var_sdd_d = sdd_fid.variables['decile_values']
        var_sdd_g = sdd_fid.variables['decile_groups']
        var_sdd_time = sdd_fid.variables['time']
        sdd_date_list = num2date(sdd_fid.variables['time'][:],
                                 units=sdd_fid.variables['time'].getncattr('units'),
                                 calendar='gregorian').tolist()

    with nc.Dataset(onc_path_file, 'r') as onc_fid:  # getting date from the nc

        onc_date_list = num2date(onc_fid.variables['time'][:],
                                 units=onc_fid.variables['time'].getncattr('units'),
                                 calendar='gregorian').tolist()

        cnt_dt = -1
        cur_month = 0
        myd_data = None
        myd_mask = 1.0
        onc_mask = 1.0
        for onc_date in onc_date_list:
            # print(onc_date)
            cnt_dt += 1

            if onc_date not in sdd_date_list:

                print('appending', onc_date)

                onc_data = np.array(onc_fid.variables[nc_var][cnt_dt, :, :])
                onc_data[onc_data == -9999.9] = np.nan

                onc_mask = copy(onc_data)
                onc_mask[~np.isnan(onc_mask)] = 1.0

                if onc_date.month > cur_month:
                    cur_month = onc_date.month

                    # here to load decile map of the corresponding month

                    myd_file = nc_var_short + '_' + str(onc_date.month) + '_dc.nc'
                    myd_path_file = myd_path + '/' + myd_file

                    with nc.Dataset(myd_path_file, 'r') as myd_fid:
                        myd_data = np.array(myd_fid.variables[nc_var + '_deciles'][:])
                        myd_data[myd_data == -9999.9] = np.nan

                        myd_mask = np.nansum(myd_data, 0)
                        myd_mask[~np.isnan(myd_mask)] = 1.0

                onc_data = onc_data[np.newaxis, :, :]
                arr_diff = np.abs(onc_data - myd_data)
                # print(arr_diff.shape)

                d_class = np.argmin(arr_diff, 0) + 1
                # print(d_class.shape)

                d_class = d_class * myd_mask * onc_mask

                d_group = copy(d_class)

                group_dict = {
                    1: 10,
                    2: 20,
                    3: 20,
                    4: 30,
                    5: 30,
                    6: 30,
                    7: 40,
                    8: 40,
                    9: 50,
                }

                for g_key, g_val in group_dict.items():
                    d_group[d_class == g_key] = g_val

                d_group = d_group / 10
                d_class[np.isnan(d_class)] = 111
                d_group[np.isnan(d_group)] = 111

                var_sdd_d[cnt_dt, :, :] = d_class
                var_sdd_g[cnt_dt, :, :] = d_group

                var_sdd_time[cnt_dt] = date2num(onc_date, units='seconds since 1970-01-01 00:00:00.0', calendar='standard')

shutil.copyfile(sdd_temp_path_file, sdd_path_file)
#os.remove(sdd_temp_path_file)
