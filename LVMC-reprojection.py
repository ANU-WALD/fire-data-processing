"""
Create a lat/lon mosaic of MODIS-derived fuel moisture for Australia.

Still experimental.
"""

import collections
import datetime
import functools
import glob
import json
import math
import os
import sys

import numpy as np
import xarray as xr

from osgeo import gdal, gdal_array, osr

sys.path.append(os.path.abspath('.'))
import onetile


# Start by setting up some utilities and constants for locations:

start_time = datetime.datetime.now()


def elapsed_time():
    return '{0:.2f} minutes'.format(
        (datetime.datetime.now() - start_time).total_seconds() / 60)


tiles = ('h28v13,h29v11,h28v12,h29v10,h29v12,h32v10,h27v11,h31v11,h32v11,'
         'h30v11,h30v10,h27v12,h30v12,h31v12,h31v10,h29v13,h28v11').split(',')

AffineGeoTransform = collections.namedtuple(
    'GeoTransform', ['origin_x', 'pixel_width', 'x_rot',
                     'origin_y', 'y_rot', 'pixel_height'])


def get_geot(ds):
    """Take an Xarray object with x and y coords; return geotransform."""
    return AffineGeoTransform(*map(float, (
        # Affine matrix - start/step/rotation, start/rotation/step - in 1D
        ds.x[0], (ds.x[-1] - ds.x[0]) / ds.x.size, 0,
        ds.y[0], 0, (ds.y[-1] - ds.y[0]) / ds.y.size
    )))


class aus:
    start_lat = -10
    stop_lat = -44
    start_lon = 113
    stop_lon = 154

out_res_degrees = 0.005

ll_geot = AffineGeoTransform(
    origin_x=aus.start_lon, pixel_width=out_res_degrees, x_rot=0,
    origin_y=aus.start_lat, y_rot=0, pixel_height=-out_res_degrees
)

new_shape = (
    math.ceil((aus.start_lat - aus.stop_lat) / out_res_degrees),
    math.ceil((aus.stop_lon - aus.start_lon) / out_res_degrees),
)

ll_coords = dict(
    latitude=np.arange(new_shape[0]) * ll_geot.pixel_height + ll_geot.origin_y,
    longitude=np.arange(new_shape[1]) * ll_geot.pixel_width + ll_geot.origin_x,
)

with open('sinusoidal.json') as f:
    wkt_str = json.load(f)['spatial_ref']


# Next, define some generically useful functions:


def project_array(array, geot):
    """Reproject a tile from Modis Sinusoidal to WGS84 Lat/Lon coordinates.
    Metadata is handled by the calling function.
    """
    # Takes around seven seconds per layer for in-memory Australia mosaics
    assert isinstance(geot, AffineGeoTransform)

    def array_to_raster(array, geot):
        ysize, xsize = array.shape  # unintuitive order, but correct!
        dataset = gdal.GetDriverByName('MEM').Create(
            '', xsize, ysize,
            eType=gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype))
        dataset.SetGeoTransform(geot)
        dataset.SetProjection(wkt_str)
        dataset.GetRasterBand(1).WriteArray(array)
        return dataset

    input_data = array_to_raster(array, geot)

    # Set up the reference systems and transformation
    from_sr = osr.SpatialReference()
    from_sr.ImportFromWkt(wkt_str)
    to_sr = osr.SpatialReference()
    to_sr.SetWellKnownGeogCS("WGS84")

    # Get new geotransform and create destination raster
    dest_arr = np.empty(new_shape)
    dest_arr[:] = np.nan
    dest = array_to_raster(dest_arr, ll_geot, to_sr.ExportToWkt())

    # Perform the projection/resampling
    gdal.ReprojectImage(
        input_data, dest,
        wkt_str, to_sr.ExportToWkt(),
        gdal.GRA_NearestNeighbour)

    return xr.DataArray(
        dest.GetRasterBand(1).ReadAsArray(),
        dims=('latitude', 'longitude'),
        coords=ll_coords)


def get_landcover_masks(year=2017):
    """Get, or calculate, the landcover masks for Australia."""
    year = int(year)
    year = min([year, 2013])
    assert year >= 2001

    fname = '/g/data/ub8/au/FMC/{}_latlon_masks.nc'.format(year)
    if os.path.isfile(fname):
        return xr.open_dataset(fname)

    masks = [onetile.get_masks(str(year), t) for t in tiles]
    forest, grass, shrub = [
        functools.reduce(
            xr.DataArray.combine_first,
            [m[key] for m in masks]
        ).fillna(0).astype('?')
        for key in ['forest', 'grass', 'shrub']
    ]
    geot = get_geot(forest)
    masks = xr.Dataset()
    masks['forest'] = project_array(forest.astype('uint8').values, geot)
    masks['grass'] = project_array(grass.astype('uint8').values, geot)
    masks['shrub'] = project_array(shrub.astype('uint8').values, geot)
    masks = masks.fillna(0).astype('?')
    masks.to_netcdf(fname)
    return masks


def get_mean_LMVC():
    """Get or calculate mean LVMC as lat/lon mosaic.

    TODO: recalculate this with c6/median (currently c6/mean).
        (requires recalculation from tiles, not just projection)

    """
    fname = '/g/data/ub8/au/FMC/c6/mean_LVMC_latlon.nc'
    if os.path.isfile(fname):
        return xr.open_dataset(fname).lvmc_mean
    base = functools.reduce(xr.DataArray.combine_first, [
        xr.open_dataset('/g/data/ub8/au/FMC/c6/mean_LVMC_{}.nc'.format(tile)).lvmc_mean
        for tile in tiles
    ])
    proj = project_array(base.values, get_geot(base))
    proj.to_netcdf('/g/data/ub8/au/FMC/c6/mean_LVMC_latlon.nc')
    return proj


def calculate_flammability(ds, year=2017):
    """Add flammability variable to a dataset."""
    ds = ds.astype('float32')
    masks = get_landcover_masks(year=year)
    diff = ds.lvmc_mean.diff('time')
    anomaly = ds.lvmc_mean - get_mean_LMVC()
    print('loaded flammability inputs ({})'.format(elapsed_time()))

    ds['flammability_index'] = ds.lvmc_mean.copy(deep=True).rename('flammability_index')
    ds.flammability_index.attrs = dict(
        comment='Unitless index of flammability',
        units='unitless',
        grid_mapping='sinusoidal',
        long_name='Flammability Index'
    )
    ds.flammability_index[:] = np.nan

    # Calculate flammability and insert into dataset
    grass = 0.18 - 0.01 * ds.lvmc_mean + 0.02 * diff - 0.02 * anomaly
    shrub = 5.66 - 0.09 * ds.lvmc_mean + 0.005 * diff - 0.28 * anomaly
    forest = 1.51 - 0.03 * ds.lvmc_mean + 0.02 * diff - 0.02 * anomaly
    print('calculated flammability components ({})'.format(elapsed_time()))
    since = -diff.time.size
    for msk, vals in [(masks.grass, grass),
                      (masks.shrub, shrub),
                          (masks.forest, forest)]:
        ds.flammability_index.values[since:] = \
            np.where(msk.values, vals, ds.flammability_index[since:])

    # Convert to [0..1] index with exponential equation
    ds.flammability_index.values[:] = 1 / (1 + np.e ** - ds.flammability_index.values)
    print('done with flammability ({})'.format(elapsed_time()))

    return ds.astype('float32')


def do_everything(year=2017):
    fname = '/g/data/ub8/au/FMC/australia_LVMC_{}.nc'.format(year)

    # TODO: check that we're using the right input files
    pattern = '/g/data/ub8/au/FMC/LVMC_new/LVMC_{}*.nc'.format(year)
    files = glob.glob(pattern)

    imgs = [xr.open_dataset(f, chunks=dict(time=1)) for f in files]
    big = functools.reduce(xr.Dataset.combine_first, imgs)
    geot = get_geot(big)
    out = xr.Dataset()

    print('Opened all files, starting projection ({})'.format(elapsed_time()))
    out['lvmc_mean'] = xr.concat(
        [project_array(big.lvmc_mean.sel(time=ts).values, geot) for ts in big.time],
        dim=big.time
    )
    print('Projected lvmc_mean ({})'.format(elapsed_time()))
    out['lvmc_stdv'] = xr.concat(
        [project_array(big.lvmc_mean.sel(time=ts).values, geot) for ts in big.time],
        dim=big.time
    )
    print('projected lvmc_stdev ({})'.format(elapsed_time()))

    final = calculate_flammability(out, year=year)
    print('calculated flammability ({})'.format(elapsed_time()))
    final.to_netcdf(fname)
    print('Finished! ({})'.format(elapsed_time()))


if __name__ == '__main__':
    do_everything()
