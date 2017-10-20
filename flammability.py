"""
Script to create one tile-year of flammability data, from the FMC products.

"""

import argparse
import os
import re

import numpy as np
import xarray as xr

from onetile import get_masks


def write_flammability(out, anomaly, diff, cover, fname):
    # Create dataset
    out['flammability_index'] = out.lvmc_mean.rename('flammability_index')
    del out['lvmc_stdv']
    out.flammability_index.attrs = dict(
        comment='Unitless index of flammability',
        units='unitless',
        grid_mapping='sinusoidal',
        long_name='Flammability Index'
    )
    out.attrs['title'] = 'Flammability Index'
    out.flammability_index.load()
    out.flammability_index[:] = np.nan

    # Calculate flammability and insert into dataset
    grass = 0.18 - 0.01 * out.lvmc_mean + 0.02 * diff - 0.02 * anomaly
    shrub = 5.66 - 0.09 * out.lvmc_mean + 0.005 * diff - 0.28 * anomaly
    forest = 1.51 - 0.03 * out.lvmc_mean + 0.02 * diff - 0.02 * anomaly
    del out['lvmc_mean']
    since = -diff.time.size
    out.flammability_index.values[since:] = np.where(
        cover['grass'], grass, out.flammability_index[since:])
    out.flammability_index.values[since:] = np.where(
        cover['shrub'], shrub, out.flammability_index[since:])
    out.flammability_index.values[since:] = np.where(
        cover['forest'], forest, out.flammability_index[since:])

    # Convert to [0..1] index with exponential equation
    out.flammability_index.values[:] = \
        1 / (1 + np.e ** - out.flammability_index.values)

    print('writing')
    out.flammability_index.encoding.update(dict(
        shuffle=True, zlib=True, chunks=dict(x=400, y=400, time=6),
        # After compression, set fill to work around GSKY transparency bug
        _FillValue=-999,
    ))
    out.to_netcdf(fname)
    os.system('chmod a+rx ' + fname)


def main(year, tile):
    fname = '/g/data/ub8/au/FMC/Flammability/Flammability_{}_{}.nc'.format(year, tile)
    if os.path.isfile(fname):
        return
    data = xr.open_mfdataset('/g/data/ub8/au/FMC/LVMC/LVMC_20??_{}.nc'.format(tile),
                             chunks=dict(time=31))
    base = xr.open_dataset('/g/data/ub8/au/FMC/c6/mean_LVMC_{}.nc'.format(tile)).lvmc_mean
    diff = dict(data.lvmc_mean.diff('time').groupby('time.year'))[year]
    anomaly = dict((data.lvmc_mean - base).groupby('time.year'))[year]
    annual = dict(data.groupby('time.year'))[year]
    cover = get_masks(year, tile)
    write_flammability(annual, anomaly, diff, cover, fname)
    print('Done!')


def get_validated_args():

    def check_year(val):
        """Validate arg and transform glob pattern to file list."""
        assert re.match(r'\A20\d\d\Z', val), repr(val)
        return int(val)

    def check_tile(val):
        """Validate that arg is tile string."""
        assert re.match(r'\Ah\d\dv\d\d\Z', val), repr(val)
        return val

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--year', type=check_year, default=os.environ.get('FMC_YEAR'),
        help='four-digit year to process')
    parser.add_argument(
        '--tile', type=check_tile, default=os.environ.get('FMC_TILE'),
        help='tile to process, "hXXvYY"')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_validated_args()
    print(args)
    main(args.year, args.tile)
