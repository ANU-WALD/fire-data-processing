import os
import sys
from netCDF4 import num2date, date2num
import netCDF4 as nc
import functions_pbs

"""
in raijin only
cd /g/data/xc0/user/ali/code/fire_deciles
/g/data/xc0/software/python/miniconda3/bin/python3 00_task_manager_nc.py flammability 2019
/g/data/xc0/software/python/miniconda3/bin/python3 00_task_manager_nc.py fmc_mean 2019

nc_var: flammability or fmc_mean
nc_year: 2019 or other years
"""

if len(sys.argv) > 1:
    nc_var = sys.argv[1]
    nc_year = sys.argv[2]
else:
    nc_var = 'flammability'
    nc_year = str(2019)

print(sys.argv)

var_short_dict = {
    'flammability': 'flam',
    'fmc_mean': 'fmc'
}
nc_var_short = var_short_dict[nc_var]

temp_path = '/g/data/xc0/project/FMC_Australia/calc_deciles/data/temp'
pbs_path = os.path.abspath('./pbs_scripts') + '/'
python_path = '/g/data/xc0/software/python/miniconda3/bin/python3'
code_path = os.getcwd()

pbs_dict = {
    '4_LGA': {
        'config': {
            'pbs_file': '4_' + nc_var + '_' + str(nc_year) + '_LGA_nc.pbs',
            'q': 'normal',
            'ncpus': 16,
            'mem': 32,
            'walltime_hr': 9
        },
        'cmd_list': ['module load netcdf',
                     'cd ' + code_path,
                     python_path + ' 04_zonal_statistics_org_nc.py ' + temp_path + ' ' + nc_var + ' ' + str(nc_year) + ' LGA'
                     ],
        'depends_on': None
    },

    '4_FWA': {
        'config': {
            'pbs_file': '4_' + nc_var + '_' + str(nc_year) + '_FWA_nc.pbs',
            'q': 'normal',
            'ncpus': 16,
            'mem': 32,
            'walltime_hr': 9
        },
        'cmd_list': ['module load netcdf',
                     'cd ' + code_path,
                     python_path + ' 04_zonal_statistics_org_nc.py ' + temp_path + ' ' + nc_var + ' ' + str(nc_year) + ' FWA'
                     ],
        'depends_on': '4_LGA'
    },
    '4_States': {
        'config': {
            'pbs_file': '4_' + nc_var + '_' + str(nc_year) + '_States_nc.pbs',
            'q': 'normal',
            'ncpus': 16,
            'mem': 32,
            'walltime_hr': 9
        },
        'cmd_list': ['module load netcdf',
                     'cd ' + code_path,
                     python_path + ' 04_zonal_statistics_org_nc.py ' + temp_path + ' ' + nc_var + ' ' + str(nc_year) + ' States'
                     ],
        'depends_on': '4_FWA'
    },
    '5': {
        'config': {
            'pbs_file': '5_' + nc_var + '_nc.pbs',
            'q': 'normal',
            'ncpus': 8,
            'mem': 16,
            'walltime_hr': 3
        },
        'cmd_list': ['module load netcdf',
                     'module load nco',
                     'cd ' + code_path,
                     python_path + ' 05_zonal_statistics_deciles_merge_to_nc_org_nc.py ' + temp_path + ' LGA ' + nc_var,
                     'cd ' + code_path,
                     python_path + ' 05_zonal_statistics_deciles_merge_to_nc_org_nc.py ' + temp_path + ' FWA ' + nc_var,
                     'cd ' + code_path,
                     python_path + ' 05_zonal_statistics_deciles_merge_to_nc_org_nc.py ' + temp_path + ' States ' + nc_var,
                     ],
        'depends_on': '4_States'
    },

}

steps = ['4_LGA', '4_FWA', '4_States', '5']

ids_path_file = pbs_path + 'jobids_nc_45_' + nc_var + '_' + str(nc_year) + '.txt'
functions_pbs.schedule_pbs(pbs_path=pbs_path, pbs_dict=pbs_dict, steps=steps, ids_path_file=ids_path_file)
