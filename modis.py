"""
General purpose functions for loading MODIS data.

This script is used for loading reflectance and restoring physical coordinates
to an array for a given tile.
"""

import re
import glob
import datetime
import typing as t
from pathlib import Path

import xarray as xr
import pandas as pd
import numpy as np

xr_data_type = t.Union[xr.Dataset, xr.DataArray]

modis_band_map = {
    'Nadir_Reflectance_Band1': 'red_630_690',
    'Nadir_Reflectance_Band2': 'nir1_780_900',
    'Nadir_Reflectance_Band3': 'blue_450_520',
    'Nadir_Reflectance_Band4': 'green_530_610',
    'Nadir_Reflectance_Band5': 'nir2_1230_1250',
    'Nadir_Reflectance_Band6': 'swir1_1550_1750',
    'Nadir_Reflectance_Band7': 'swir2_2090_2350',
}


def add_tile_coords(tile: str, dataset: xr_data_type) -> xr_data_type:
    """Restore physical coordinates to dataset."""
    scale = 1111950.5196669996
    regex = re.compile('h\d+v\d+')
    matches = regex.findall(tile)
    extract = re.compile('\d+')
    h, v = extract.findall(matches[0])
    h = int(h)
    v = int(v)
    x_start = scale * (h - 18)
    x_end = scale * (h - 17)
    y_start = -scale * (v - 9)
    y_end = -scale * (v - 8)
    dataset['x'] = xr.IndexVariable('x', np.linspace(x_start, x_end, 2400))
    dataset['y'] = xr.IndexVariable('y', np.linspace(y_start, y_end, 2400))
    return dataset


def difference_index(a: xr.DataArray, b: xr.DataArray) -> xr.DataArray:
    """Get difference index between bands used in NDVI, NDII, etc."""
    return ((a - b) / (a + b)).astype('float32')


reflectance_file_cache = []  # type: t.List[str]


def get_reflectance(year: int, tile: str) -> xr.Dataset:
    """Load reflectance data for one tile-year."""
    global reflectance_file_cache
    if not reflectance_file_cache:
        reflectance_file_cache[:] = sorted(glob.glob(
            '/g/data/u39/public/data/modis/lpdaac-tiles-c6/MCD43A4.006/' +
            '{year}.??.??/MCD43A4.A{year}???.h??v??.006.*.hdf'
            .format(year=year)
        ))
    files = [f for f in reflectance_file_cache if tile in Path(f).stem]
    pattern = re.compile(r'MCD43A4.A\d{4}(?P<day>\d{3}).h\d\dv\d\d.006.\d+'
                         '.hdf')
    dates, parts = [], []
    for f in files:
        try:
            parts.append(xr.open_dataset(f, chunks=2400))
            day, = pattern.match(Path(f).stem).groups()
            dates.append(datetime.date(int(year), 1, 1) +
                         datetime.timedelta(days=int(day) - 1))
        except Exception:
            print('Could not read from ' + f)

    date_series = pd.to_datetime(dates)
    date_series.name = 'time'

    ds = xr.concat(parts, date_series)
    out = xr.Dataset()
    for i in map(str, range(1, 8)):
        key = 'Nadir_Reflectance_Band' + i
        data_ok = ds['BRDF_Albedo_Band_Mandatory_Quality_Band' + i] == 0
        out[modis_band_map[key]] = ds[key].where(data_ok).astype('f4')
    out['ndvi_ok_mask'] = 0.15 < difference_index(
        out.nir1_780_900, out.red_630_690)
    out['ndii'] = difference_index(out.nir1_780_900, out.swir1_1550_1750)

    xy_names = {'YDim:MOD_Grid_BRDF': 'y', 'XDim:MOD_Grid_BRDF': 'x'}

    try:
        out.rename(xy_names, inplace=True)
    except ValueError:
        pass
    out.time.encoding.update(dict(
        units='days since 1900-01-01', calendar='gregorian', dtype='i4'))
    return add_tile_coords(tile, out)


def get_masks(year: int, tile: str) -> t.Dict[str, xr.DataArray]:
    """Get landcover masks for one tile-year."""
    file, = glob.glob(
        '/g/data/u39/public/data/modis/lpdaac-tiles-c5/MCD12Q1.051/' +
        '{year}.??.??/MCD12Q1.A{year}???.{tile}.051.*.hdf'
        .format(year=min(int(year), 2013), tile=tile)
    )
    arr = xr.open_dataset(file).Land_Cover_Type_1
    classes = {
        'grass': (u'grasslands', u'croplands'),
        'shrub': (u'closed shrubland', u'open shrublands'),
        'forest': (
            u'evergreen needleleaf forest', u'evergreen broadleaf forest',
            u'deciduous needleleaf forest', u'deciduous broadleaf forest',
            u'mixed forests', u'woody savannas', u'savannas'),
    }  # type: t.Dict[str, t.Tuple[str, ...]]
    masks = {
        k: np.sum((arr == arr.attrs[name]) for name in v).astype(bool)
        for k, v in classes.items()
    }

    xy_names = {'YDim:MOD12Q1': 'y', 'XDim:MOD12Q1': 'x'}

    return {k: add_tile_coords(tile, v.rename(xy_names))
            for k, v in masks.items()}
