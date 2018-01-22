import json
import xarray as xr

with open('tiles.json') as f:
    tiles = list(json.load(f))

for tile in tiles:
    infile = '/g/data/ub8/au/FMC/LVMC_new/LVMC_20??_{}.nc'.format(tile)
    outfile = '/g/data/ub8/au/FMC/mean_LVMC_{}.nc'.format(tile)
    xr.open_mfdataset(infile).mean(dim='time').to_netcdf(outfile)
