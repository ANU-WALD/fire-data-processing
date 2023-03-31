import os
import sys
from netCDF4 import num2date, date2num
import netCDF4 as nc
import functions_pbs

"""
in raijin only
cd /g/data/xc0/user/ali/code/fire_deciles
/g/data/xc0/software/python/miniconda3/bin/python3 00_task_manager_dc.py flammability 2019 345
/g/data/xc0/software/python/miniconda3/bin/python3 00_task_manager_dc.py fmc_mean 2019 345

nc_var: flammability or fmc_mean
nc_year: 2019 or other years
var_mode: '345' for all tasks or '45'. see pbs_dict for task ids
"""

if len(sys.argv) > 1:
    nc_var = sys.argv[1]
    nc_year = sys.argv[2]
    var_mode = sys.argv[3]
else:
    nc_var = 'flammability'
    nc_year = str(2019)
    var_mode = '345'

print(nc_var, nc_var, var_mode)

var_short_dict = {
    'flammability': 'flam',
    'fmc_mean': 'fmc'
}
nc_var_short = var_short_dict[nc_var]

sdd_path = '/g/data/ub8/au/FMC/c6/mosaics/deciles'
sdd_file = nc_var_short + '_c6_' + nc_year + '_dc.nc'

sdd_path_file = sdd_path + '/' + sdd_file
onc_path_file = '/g/data/ub8/au/FMC/c6/mosaics/' + nc_var_short + '_c6_' + nc_year + '.nc'

with nc.Dataset(onc_path_file, 'r') as onc_fid:
    onc_last_date = num2date(onc_fid.variables['time'][:],
                             units=onc_fid.variables['time'].getncattr('units'),
                             calendar='gregorian').tolist()[-1]

with nc.Dataset(sdd_path_file, 'r') as sdd_fid:
    sdd_last_date = num2date(sdd_fid.variables['time'][:],
                             units=sdd_fid.variables['time'].getncattr('units'),
                             calendar='gregorian').tolist()[-1]

temp_path = '/g/data/xc0/project/FMC_Australia/calc_deciles/data/temp'
pbs_path = os.path.abspath('./pbs_scripts') + '/'
python_path = '/g/data/xc0/software/python/miniconda3/bin/python3'
code_path = os.getcwd()

pbs_dict = {
    '3': {
        'config': {
            'pbs_file': '3_' + nc_var + '_' + str(nc_year) + '.pbs',
            'q': 'normal',
            'ncpus': 8,
            'mem': 16,
            'walltime_hr': 1
        },
        'cmd_list': ['module load netcdf',
                     'cd ' + code_path,
                     python_path + ' 03_calc_single_year_deciles.py ' + nc_var + ' ' + temp_path + ' ' + str(nc_year)
                     ],
        'depends_on': None
    },

    '4_LGA': {
        'config': {
            'pbs_file': '4_' + nc_var + '_' + str(nc_year) + '_LGA.pbs',
            'q': 'normal',
            'ncpus': 16,
            'mem': 32,
            'walltime_hr': 9
        },
        'cmd_list': ['module load netcdf',
                     'cd ' + code_path,
                     python_path + ' 04_zonal_statistics_deciles.py ' + temp_path + ' ' + nc_var + ' ' + str(nc_year) + ' LGA'
                     ],
        'depends_on': '3'
    },

    '4_FWA': {
        'config': {
            'pbs_file': '4_' + nc_var + '_' + str(nc_year) + '_FWA.pbs',
            'q': 'normal',
            'ncpus': 16,
            'mem': 32,
            'walltime_hr': 9
        },
        'cmd_list': ['module load netcdf',
                     'cd ' + code_path,
                     python_path + ' 04_zonal_statistics_deciles.py ' + temp_path + ' ' + nc_var + ' ' + str(nc_year) + ' FWA'
                     ],
        'depends_on': '4_LGA'
    },
    '4_States': {
        'config': {
            'pbs_file': '4_' + nc_var + '_' + str(nc_year) + '_States.pbs',
            'q': 'normal',
            'ncpus': 16,
            'mem': 32,
            'walltime_hr': 9
        },
        'cmd_list': ['module load netcdf',
                     'cd ' + code_path,
                     python_path + ' 04_zonal_statistics_deciles.py ' + temp_path + ' ' + nc_var + ' ' + str(nc_year) + ' States'
                     ],
        'depends_on': '4_FWA'
    },
    '5': {
        'config': {
            'pbs_file': '5_' + nc_var + '.pbs',
            'q': 'normal',
            'ncpus': 8,
            'mem': 16,
            'walltime_hr': 3
        },
        'cmd_list': ['module load netcdf',
                     'module load nco',
                     'cd ' + code_path,
                     python_path + ' 05_zonal_statistics_deciles_merge_to_nc.py ' + temp_path + ' LGA ' + nc_var,
                     'cd ' + code_path,
                     python_path + ' 05_zonal_statistics_deciles_merge_to_nc.py ' + temp_path + ' FWA ' + nc_var,
                     'cd ' + code_path,
                     python_path + ' 05_zonal_statistics_deciles_merge_to_nc.py ' + temp_path + ' States ' + nc_var,
                     ],
        'depends_on': '4_States'
    },

}

print('onc_last_date', onc_last_date)
print('sdd_last_date', sdd_last_date)

if var_mode == '345':
    print('in 345')
    if onc_last_date > sdd_last_date:
        print('in progress for 345')
        steps = ['3', '4_LGA', '4_FWA', '4_States',  '5']
        ids_path_file = pbs_path + 'jobids_dc_345_' + nc_var + '_' + str(nc_year) + '.txt'
        functions_pbs.schedule_pbs(pbs_path=pbs_path, pbs_dict=pbs_dict, steps=steps, ids_path_file=ids_path_file)

if var_mode == '45':
    print('in 45')
    steps = ['4_LGA', '4_FWA', '4_States', '5']

    pbs_dict['4_LGA']['depends_on'] = None

    ids_path_file = pbs_path + 'jobids_dc_45_' + nc_var + '_' + str(nc_year) + '.txt'
    functions_pbs.schedule_pbs(pbs_path=pbs_path, pbs_dict=pbs_dict, steps=steps, ids_path_file=ids_path_file)
