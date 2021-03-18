import xarray as xr
import numpy as np
import pandas as pd


lfmc_days_of_year = [i for i in range(1,366,4)]

au_tiles = ['h27v11', 'h27v12', 'h28v11', 'h28v12', 'h28v13', 'h29v10', 'h29v11', 'h29v12', 'h29v13', 'h30v10', 'h30v11', 'h30v12', 'h31v10', 'h31v11', 'h31v12', 'h32v10', 'h32v11']

year_start = 2001
year_end = 2020

for au_tile in au_tiles:
    for doy in lfmc_days_of_year:

        list_lfmc_same_doy = list()
        
        for year in range(year_start,year_end+1):

            tile = xr.open_dataset('/g/data/ub8/au/FMC/c6/fmc_c6_{0}_{1}.nc'.format(year, au_tile))

            for d in tile.time.data:

                doy_d = pd.to_datetime(d).dayofyear

                if doy_d == doy:

                    print('adding doy array ', au_tile, year, d, doy)

                    lfmc_array = tile.sel(time=d).lfmc_mean.data
                    list_lfmc_same_doy.append(lfmc_array)

        lfmc_same_doy_3d = np.dstack(list_lfmc_same_doy)
        lfmc_same_doy_mean = np.nanmean(lfmc_same_doy_3d, axis=2)
        np.savez_compressed('/g/data/ub8/au/FMC/mean_lfmc_arrays/mean_fmc_{0}_{1}_{2}_{3}.npz'.format(year_start, year_end, au_tile, doy), lfmc_mean=lfmc_same_doy_mean)

print('done')



