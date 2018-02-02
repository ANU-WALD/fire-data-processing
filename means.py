"""Calculate mean LVMC between 2001 and 2015."""

# TODO: add cmd-line to select input data, output dir, etc.

import xarray as xr

from launchmany import shortcuts

base_dir = '/g/data/ub8/au/FMC'

if __name__ == '__main__':
    for tile in shortcuts['australia'].split(','):
        infile = f'{base_dir}/LVMC/LVMC_20??_{tile}.nc'
        outfile = f'{base_dir}/mean_LVMC_{tile}.nc'
        period = slice('2001', '2015')  # type: ignore
        xr.open_mfdataset(infile, chunks=dict(time=12))\
            .sel(time=period)\
            .mean(dim='time')\
            .to_netcdf(outfile)
