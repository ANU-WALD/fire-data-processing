import xarray as xr
import numpy as np
from datetime import datetime


lfmc_days_of_year = [i for i in range(1,366,4)]

au_tiles = ['h27v11', 'h27v12', 'h28v11', 'h28v12', 'h28v13', 'h29v10', 'h29v11', 'h29v12', 'h29v13', 'h30v10', 'h30v11', 'h30v12', 'h31v10', 'h31v11', 'h31v12', 'h32v10', 'h32v11']

year_start = 2001
year_end = 2022

for au_tile in au_tiles:
    for doy in lfmc_days_of_year:
        print(au_tile, doy)

        list_lfmc_same_doy = list()
        
        for year in range(year_start,year_end+1):

            tile = xr.open_dataset('/g/data/ub8/au/FMC/tiles/fmc_c6_{0}_{1}.nc'.format(year, au_tile)) 

            d = datetime.strptime('{0}{1}'.format(year,doy), '%Y%j').strftime('%Y-%m-%d')

            try:
                lfmc_array = tile.sel(time=d).lfmc_median.data
                list_lfmc_same_doy.append(lfmc_array)

            except:
                print(d)
                pass

        lfmc_same_doy_3d = np.dstack(list_lfmc_same_doy)
        lfmc_same_doy_mean = np.nanmean(lfmc_same_doy_3d, axis=2)
        np.savez_compressed('/g/data/ub8/au/FMC/intermediary_files/mean_lfmc_arrays/mean_lfmc_{0}_{1}_{2}_{3}.npz'.format(year_start, year_end, au_tile, doy), mean_lfmc=lfmc_same_doy_mean)

print('done')
