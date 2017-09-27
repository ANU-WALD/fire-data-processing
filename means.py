import json
import xarray as xr

with open('tiles.json') as f:
    tiles = list(json.load(f))

for tile in tiles:
    infile = '/g/data/ub8/au/FMC/c6/LVMC_20??_{}.nc'.format(tile)
    outfile = '/g/data/ub8/au/FMC/c6/mean_LVMC_{}.nc'.format(tile)
    xr.open_mfdataset(infile).mean(dim='time').to_netcdf(outfile)

