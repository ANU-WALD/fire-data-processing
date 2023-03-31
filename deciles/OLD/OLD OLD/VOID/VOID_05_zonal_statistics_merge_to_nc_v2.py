import os
import sys
import glob
import pandas as pd
import numpy as np
from functions_io import load_pickle

# /g/data/xc0/software/python/miniconda3/bin/python3 VOID_05_zonal_statistics_merge_to_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp LGA11aAust flammability


# temp_path = sys.argv[1]
# plg_source = sys.argv[2]
# nc_var = sys.argv[3]

temp_path = '/g/data/xc0/project/FMC_Australia/calc_deciles/data/temp'
nc_var = 'fmc_mean'
plg_source = 'LGA11aAust'

var_short_dict = {
    'flammability': 'flam',
    'fmc_mean': 'fmc'
}
nc_var_short = var_short_dict[nc_var]

temp_path += '/' + nc_var_short

zst_temp_path = temp_path + '/zonal_stats'

zst_nc_path_file = '/g/data/ub8/au/FMC/c6/mosaics/deciles/zonal_stats' + '/' + plg_source + '_' + nc_var_short + '_zonal_stat.nc'
zst_csv_path_file = '/g/data/ub8/au/FMC/c6/mosaics/deciles/zonal_stats' + '/' + plg_source + '_' + nc_var_short + '_zonal_stat.csv'

zst_nc_temp_path_file0 = zst_temp_path + '/' + plg_source + '_' + nc_var_short + '_zonal_stat_time_double.nc'
zst_nc_temp_path_file = zst_temp_path + '/' + plg_source + '_' + nc_var_short + '_zonal_stat.nc'

zst_list = []
zst_temp_path_files = glob.glob(zst_temp_path + '/*_dc_zonal_stat.pk')
for zst_temp_path_file in zst_temp_path_files:
    zst_list.append(load_pickle(zst_temp_path_file))

df_dict = {}

min_list_all = []
max_list_all = []
avg_list_all = []
dt_list_all = []
plg_list_all = []

for plg_id in zst_list[0].keys():

    plg_list, dt_list, min_list, max_list, avg_list = [], [], [], [], []
    for zst_dict in zst_list:
        for dt, sd in zst_dict[plg_id].items():
            dt_list.append(dt)
            min_list.append(sd['min'])
            max_list.append(sd['max'])
            avg_list.append(sd['avg'])
            plg_list.append(int(plg_id))

    min_list_all.extend(min_list)
    max_list_all.extend(max_list)
    avg_list_all.extend(avg_list)
    dt_list_all.extend(dt_list)
    plg_list_all.extend(plg_list)


pd.DataFrame(data={'plg_id': plg_list_all, 'time': dt_list_all, 'min': min_list_all, 'avg': avg_list_all, 'max': max_list_all}).set_index('time').to_csv(zst_csv_path_file)
pd.DataFrame(data={'plg_id': plg_list_all, 'time': dt_list_all, 'min': min_list_all, 'avg': avg_list_all, 'max': max_list_all}).set_index(['time', 'plg_id']).to_xarray().to_netcdf(zst_nc_temp_path_file0)

# module load cdo
cmd_ncap2 = "ncap2 -s 'time=float(time);plg_id=float(plg_id);min=float(min);max=float(max);avg=float(avg)' " + zst_nc_temp_path_file0 + " " + zst_nc_temp_path_file
print(cmd_ncap2)
