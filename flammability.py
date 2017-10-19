"""
Script to create one tile-archive of flammability data, from the FMC products.

"""

import argparse
import os
import re

import numpy as np
import xarray as xr


def get_cover(year, tile, y, x):
    cover = xr.open_dataset('/g/data/xc0/user/HatfieldDodds/FMC/landcover.{}.{}.nc'.format(max([year, 2013]), tile))
    cover['y'] = y
    cover['x'] = x
    cover['grass'] = sum((cover.Land_Cover_Type_1 == i) for i in (10, 12)).astype(bool)
    cover['shrub'] = sum((cover.Land_Cover_Type_1 == i) for i in (6, 7)).astype(bool)
    cover['forest'] = sum((cover.Land_Cover_Type_1 == i) for i in (1, 2, 3, 4, 5, 8, 9)).astype(bool)
    del cover['Land_Cover_Type_1']
    return cover


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

    def fx(x):
        return 1 / (1 + np.e ** - x)
    # Calculate flammability and insert into dataset
    grass = fx(0.18 - 0.01 * out.lvmc_mean + 0.02 * diff - 0.02 * anomaly)
    shrub = fx(5.66 - 0.09 * out.lvmc_mean + 0.005 * diff - 0.28 * anomaly)
    forest = fx(1.51 - 0.03 * out.lvmc_mean + 0.02 * diff - 0.02 * anomaly)
    del out['lvmc_mean']
    since = -diff.time.size
    out.flammability_index.values[since:] = np.where(
        cover.grass, grass, out.flammability_index[since:])
    out.flammability_index.values[since:] = np.where(
        cover.shrub, shrub, out.flammability_index[since:])
    out.flammability_index.values[since:] = np.where(
        cover.forest, forest, out.flammability_index[since:])
    print('writing')
    out.to_netcdf(fname)
    os.system('chmod a+rx ' + fname)


def main(tile):
    data = xr.open_mfdataset('/g/data/ub8/au/FMC/c6/LVMC_20??_{}.nc'.format(tile),
                             chunks=dict(time=31))
    base = xr.open_dataset('/g/data/ub8/au/FMC/c6/mean_LVMC_{}.nc'.format(tile)).lvmc_mean
    diffs = dict(data.lvmc_mean.diff('time').groupby('time.year'))
    anomalies = dict((data.lvmc_mean - base).groupby('time.year'))
    annual = dict(data.groupby('time.year'))
    for year in range(2001, 2018):
        print(year, end='...   ')
        fname = '/g/data/ub8/au/FMC/c6/Flammability_{}_{}.nc'.format(year, tile)
        if os.path.isfile(fname):
            continue
        cover = get_cover(year, tile, y=base.y, x=base.x)
        write_flammability(annual[year], anomalies[year], diffs[year], cover, fname)
    print('Done!')


def get_validated_args():

    def check_tile(val):
        """Validate that arg is an existing directory."""
        assert re.match(r'\Ah\d\dv\d\d\Z', val), repr(val)
        return val

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--tile', type=check_tile, default=os.environ.get('FMC_TILE'),
        help='tile to process, "hXXvYY"')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_validated_args()
    print(args)
    main(args.tile)
