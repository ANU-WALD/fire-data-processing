import os
import glob
import shutil
import sys

# /g/data/xc0/software/python/miniconda3/bin/python3 01_nc_by_month.py flammability /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp
# /g/data/xc0/software/python/miniconda3/bin/python3 01_nc_by_month.py fmc_mean /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp

nc_var = sys.argv[1]
temp_path = sys.argv[2]

# nc_var = 'flammability'
# temp_path = '/g/data/xc0/project/FMC_Australia/calc_deciles/data/temp'

var_short_dict = {
    'flammability': 'flam',
    'fmc_mean': 'fmc'
}

nc_var_short = var_short_dict[nc_var]

temp_path += '/' + nc_var_short

if not os.path.exists(temp_path):
    os.mkdir(temp_path)

nc_org_path = '/g/data/ub8/au/FMC/c6/mosaics'
nc_org_path_files = glob.glob(nc_org_path + '/' + nc_var_short + '*.nc')

for month in range(1, 13):

    nc_merge_path_file = temp_path + '/' + nc_var_short + '_' + str(month) + '.nc'

    if not os.path.exists(nc_merge_path_file):
        temp_path_month = temp_path + '/' + nc_var_short + '_' + str(month)
        if not os.path.exists(temp_path_month):
            os.makedirs(temp_path_month)
        for nc_org_path_file in sorted(nc_org_path_files):
            nc_org_file = os.path.basename(nc_org_path_file)
            nc_org_year = int(nc_org_file.replace('.nc', '')[-4:])

            nc_sel_temp_path_file = temp_path_month + '/' + str(nc_org_year) + '_temp.nc'
            nc_sel_path_file = temp_path_month + '/' + str(nc_org_year) + '.nc'

            if not os.path.exists(nc_sel_path_file):
                cdo_cmd = '/bin/bash -c "module load cdo; cdo -selmonth,' + str(month) + ' ' + nc_org_path_file + ' ' + nc_sel_temp_path_file + '"'
                print(cdo_cmd)
                os.system(cdo_cmd)
                cdo_cmd = '/bin/bash -c "module load cdo; cdo -selname,' + nc_var + ' ' + nc_sel_temp_path_file + ' ' + nc_sel_path_file + '"'
                print(cdo_cmd)
                os.system(cdo_cmd)
                if os.path.exists(nc_sel_temp_path_file):
                    os.remove(nc_sel_temp_path_file)

        temp_path_month = temp_path + '/' + nc_var_short + '_' + str(month)
        nc_month_path_files = glob.glob(temp_path_month + '/*.nc')

        nc_month_path_files_str = ''
        for nc_month_path_file in sorted(nc_month_path_files):
            nc_month_path_files_str += ' ' + nc_month_path_file

        cdo_cmd = '/bin/bash -c "module load cdo; cdo mergetime ' + nc_month_path_files_str + ' ' + nc_merge_path_file + '"'
        print(cdo_cmd)
        os.system(cdo_cmd)
        shutil.rmtree(temp_path_month)
