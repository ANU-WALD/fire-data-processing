import numpy as np
from functions_io import load_pickle
import datetime
pk_path_file = '/g/data/xc0/project/FMC_Australia/calc_deciles/data/temp/fmc/zonal_stats/fmc_c6_2018_dc_zonal_stat.pk'

zst_dict = load_pickle(pk_path_file)

for key, val in zst_dict.items():

    print(key, val[datetime.datetime(2018, 8, 1, 0, 0)]['avg'])

