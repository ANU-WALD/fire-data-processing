import os
import sys
import glob
import shutil
import pandas as pd

from functions_io import load_pickle

# module load nco
# /g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp LGA fmc_mean
# /g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp FWA fmc_mean
# /g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp LGA flammability
# /g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp FWA flammability


temp_path = sys.argv[1]
plg_name = sys.argv[2]
nc_var = sys.argv[3]

# temp_path = '/g/data/xc0/project/FMC_Australia/calc_deciles/data/temp'
# plg_name = 'LGA'  # LGA or FWA or States
# nc_var = 'flammability'

var_short_dict = {
    'flammability': 'flam',
    'fmc_mean': 'fmc'
}
nc_var_short = var_short_dict[nc_var]

temp_path += '/' + nc_var_short

zst_temp_path = temp_path + '/zonal_stats'

zst_nc_path_file = '/g/data/ub8/au/FMC/c6/mosaics/deciles/zonal_stats' + '/' + plg_name + '_' + nc_var_short + '_zonal_stat.nc'
zst_csv_path_file = '/g/data/ub8/au/FMC/c6/mosaics/deciles/zonal_stats' + '/' + plg_name + '_' + nc_var_short + '_zonal_stat.csv'

zst_nc_temp_path_file0 = zst_temp_path + '/' + plg_name + '_' + nc_var_short + '_zonal_stat_time_double.nc'
zst_nc_temp_path_file = zst_temp_path + '/' + plg_name + '_' + nc_var_short + '_zonal_stat.nc'

if os.path.exists(zst_nc_temp_path_file0):
    os.remove(zst_nc_temp_path_file0)

if os.path.exists(zst_nc_temp_path_file):
    os.remove(zst_nc_temp_path_file)

zst_csv_temp_path_file = zst_temp_path + '/' + plg_name + '_' + nc_var_short + '_zonal_stat.csv'

zst_list = []
zst_temp_path_files = glob.glob(zst_temp_path + '/*' + plg_name + '*__dc_zonal_stat.pk')
for zst_temp_path_file in zst_temp_path_files:
    zst_list.append(load_pickle(zst_temp_path_file))

df_dict = {}

dt_list_all = []
plg_list_all = []

merge_dict = {}

stat_keys = ['coverage', 'min', 'max', 'avg', 'coverage_0', 'min_0', 'max_0', 'avg_0', 'coverage_1', 'min_1', 'max_1', 'avg_1', 'coverage_2', 'min_2', 'max_2', 'avg_2', 'coverage_3', 'min_3', 'max_3', 'avg_3']

for stat_key in stat_keys:
    merge_dict[stat_key] = []

for plg_id in zst_list[0].keys():

    dt_list, plg_list = [], []
    plg_stats = {}
    for stat_key in stat_keys:
        plg_stats[stat_key] = []

    for zst_dict in zst_list:
        for dt, sd in zst_dict[plg_id].items():

            dt_list.append(dt)
            for stat_key in stat_keys:
                plg_stats[stat_key].append(sd[stat_key])
            plg_list.append(int(plg_id))

    for stat_key in stat_keys:
        merge_dict[stat_key].extend(plg_stats[stat_key])

    dt_list_all.extend(dt_list)
    plg_list_all.extend(plg_list)

data = {
    'plg_id': plg_list_all,
    'time': dt_list_all
}

for stat_key in stat_keys:
    data[stat_key] = merge_dict[stat_key]

pd.DataFrame(data=data).set_index('time').to_csv(zst_csv_temp_path_file)
pd.DataFrame(data=data).set_index(['time', 'plg_id']).to_xarray().to_netcdf(zst_nc_temp_path_file0)

ncap2_vars = 'time=float(time);plg_id=float(plg_id);'
for stat_key in stat_keys:
    ncap2_vars += stat_key + '=float(' + stat_key + ');'
ncap2_vars = ncap2_vars[:-1]

cmd_ncap2 = "ncap2 -s '" + ncap2_vars + "' " + zst_nc_temp_path_file0 + " " + zst_nc_temp_path_file
print(cmd_ncap2)
os.system(cmd_ncap2)

print(zst_nc_path_file)
shutil.copyfile(zst_nc_temp_path_file, zst_nc_path_file)
