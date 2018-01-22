"""
Script to create one tile-year of LFMC data, from the original MODIS products.

Likely to remain a (useful) work in progress for some time.

Requires PyNIO to read MODIS .hdf files, and therefore Python 2 for now.

It's also a best-possible port of equations developed for MODIS C5 to C6 data;
we plan to fully upgrade in future but that will require revalidation.

"""

import os
import re
import json
import glob
import modis
import shutil
import argparse
import datetime

import numpy as np
import pandas as pd
import xarray as xr


__version__ = '0.3.0'

bands_to_use = {'MODIS': ['red_630_690', 'nir1_780_900', 'green_530_610',
                          'swir1_1550_1750', 'swir2_2090_2350', 'ndii'],
                'SPOT6': ['band_0_blue', 'band_1_green', 'band_2_red',
                          'band_3_nir'],
                'SPOT7': ['band_0_blue', 'band_1_green', 'band_2_red',
                          'band_3_nir'],
                }

functor_cache = {}


def get_functor(veg_type, satellite):
    """Returns a function to get the mean and stdev of LFMC for the top n
    values.

    Note that the function object is cached to avoid loading the vmat and smat
    tables more than once per vegetation type.
    """
    assert satellite in ['MODIS', 'SPOT6', 'SPOT7'], 'Satellite does not exist'

    if (veg_type, satellite) in functor_cache:
        return functor_cache[(veg_type, satellite)]

    # Get the lookup table
    if satellite == 'MODIS':
        merged_lookup = pd.read_csv(
                        'lookup_tables/merged_lookup.csv', index_col='ID')
        merged_lookup['ndii'] = modis.difference_index(
            merged_lookup.nir1_780_900, merged_lookup.swir1_1550_1750)
        table = merged_lookup.where(merged_lookup.VEGTYPE == veg_type)
    elif satellite == 'SPOT6':
        merged_lookup = pd.read_csv('lookup_tables/SPOT6_lookup.csv')
        table = merged_lookup.where(merged_lookup.landcover == veg_type)
    elif satellite == 'SPOT7':
        merged_lookup = pd.read_csv('lookup_tables/SPOT7_lookup.csv')
        table = merged_lookup.where(merged_lookup.landcover == veg_type)

    vmat = table[bands_to_use[satellite]].values
    vsmat = np.sqrt((vmat ** 2).sum(axis=1))

    print(satellite)
    fmc = table['fmc' if 'SPOT' in satellite else 'FMC'].values

    def get_top_n(mb, vmat=vmat, vsmat=vsmat, fmc=fmc):
        spectral_angle = np.arccos(
            np.einsum('ij,j->i', vmat, mb) /
            (np.sqrt(np.einsum('i,i->', mb, mb)) * vsmat)
        )
        top_values = fmc[np.argpartition(spectral_angle, 40)[:40]]
        return np.median(top_values, axis=-1), top_values.std(axis=-1)

    functor_cache[(veg_type, satellite)] = get_top_n
    return get_top_n


def get_fmc(dataset, masks=None, satellite='MODIS'):
    """Get the mean and stdev of LFMC for the given Xarray dataset
    (one time-step)."""
    if satellite == 'MODIS':
        bands = xr.concat([dataset[b] for b in bands_to_use[satellite]],
                          dim='band')
    else:
        bands = dataset.radiance
        if masks is None:
            masks = dict(
                # assume it's all forest in Namadgi, as no landcover layer
                forest=np.ones((bands.y.size, bands.x.size), dtype=bool),
            )
        if not hasattr(dataset, 'ndvi_ok_mask'):
            red = dataset.radiance.sel(band=3)
            nir = dataset.radiance.sel(band=4)
            dataset['ndvi_ok_mask'] = ((nir - red) / (nir + red)) > 0.15
    assert masks is not None
    ok = np.logical_and(dataset.ndvi_ok_mask, bands.notnull().all(dim='band'))

    out = np.full((2,) + ok.shape, np.nan, dtype='float32')

    for kind, mask in masks.items():
        cond = np.logical_and(ok, mask[:bands.y.size, :bands.x.size]).values
        vals = bands.transpose('band', 'y', 'x').values[:, cond]
        if vals.size:
            # Only calculate for and assign to the unmasked values
            out[:, cond] = np.apply_along_axis(
                            get_functor(kind, satellite), 0, vals)

    data_vars = dict(lvmc_mean=(('y', 'x'), out[0]),
                     lvmc_stdv=(('y', 'x'), out[1]))
    return xr.Dataset(data_vars=data_vars, coords=dataset.coords)


reflectance_file_cache = []


def get_reflectance(year, tile):
    global reflectance_file_cache
    if not reflectance_file_cache:
        reflectance_file_cache[:] = sorted(glob.glob(
            '/g/data/u39/public/data/modis/lpdaac-tiles-c6/MCD43A4.006/' +
            '{year}.??.??/MCD43A4.A{year}???.h??v??.006.*.hdf'
            .format(year=year)
        ))
    files = [f for f in reflectance_file_cache if tile in os.path.basename(f)]
    pattern = re.compile(r'MCD43A4.A\d{4}(?P<day>\d{3}).h\d\dv\d\d.006.\d+'
                         '.hdf')
    dates, parts = [], []
    for f in files:
        try:
            parts.append(xr.open_dataset(f, chunks=2400))
            day, = pattern.match(os.path.basename(f)).groups()
            dates.append(datetime.date(int(year), 1, 1) +
                         datetime.timedelta(days=int(day) - 1))
        except Exception:
            print('Could not read from ' + f)

    dates = pd.to_datetime(dates)
    dates.name = 'time'

    ds = xr.concat(parts, dates)
    out = xr.Dataset()
    for i in map(str, range(1, 8)):
        key = 'Nadir_Reflectance_Band' + i
        data_ok = ds['BRDF_Albedo_Band_Mandatory_Quality_Band' + i] == 0
        out[modis.modis_band_map[key]] = ds[key].where(data_ok).astype('f4')
    out['ndvi_ok_mask'] = 0.15 < modis.difference_index(
                                        out.nir1_780_900, out.red_630_690)
    out['ndii'] = modis.difference_index(out.nir1_780_900, out.swir1_1550_1750)

    out.rename({'YDim:MOD_Grid_BRDF': 'y',
                'XDim:MOD_Grid_BRDF': 'x'}, inplace=True)
    out.time.encoding.update(dict(
        units='days since 1900-01-01', calendar='gregorian', dtype='i4'))
    return out


def get_masks(year, tile):
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
    }
    masks = {
        k: np.sum((arr == arr.attrs[name]) for name in v).astype(bool)
        for k, v in classes.items()
    }
    return {k: add_tile_coords(tile, v.rename({'YDim:MOD12Q1': 'y',
                                               'XDim:MOD12Q1': 'x'}))
            for k, v in masks.items()}


def add_tile_coords(tile, dataset):
    scale = 1111950.5196669996

    # regex to match string
    regex = re.compile('h\d+v\d+')
    matches = regex.findall(tile)

    # extract values from string
    extract = re.compile('\d+')
    h, v = extract.findall(matches[0])
    h = int(h)
    v = int(v)

    # calculate start and end values
    x_start = scale * (h - 18)
    x_end = scale * (h - 17)

    y_start = -scale * (v - 9)
    y_end = -scale * (v - 8)

    dataset['x'] = xr.IndexVariable('x', np.linspace(x_start, x_end, 2400))
    dataset['y'] = xr.IndexVariable('y', np.linspace(y_start, y_end, 2400))
    return dataset


def main(year, tile, output_path):
    out_file = os.path.join(output_path, 'LVMC_{}_{}.nc'.format(year, tile))
    # Get the landcover masks
    masks = get_masks(year, tile)
    # Get the main dataset - demo is one tile for a year
    ds = get_reflectance(year, tile)

    if not os.path.isfile(out_file):
        # Create all output data
        out = xr.concat(
            [get_fmc(ds.sel(time=ts), masks) for ts in ds.time], dim='time')
    else:
        # Create only missing output data
        existing = xr.open_dataset(out_file)
        assert np.all(ds.time[:len(existing.time)] == existing.time)
        if len(existing.time) == len(ds.time):
            print('No new input data')
            return
        new_data = xr.concat(
            [get_fmc(ds.sel(time=ts), masks)
             for ts in ds.time[len(existing.time):]], dim='time')
        add_tile_coords(tile, new_data)
        out = xr.merge([existing, new_data])

    with open('nc_metadata.json') as f:
        json_attrs = json.load(f)

    # Add metadata to the resulting file
    out.attrs.update(json_attrs)

    out.lvmc_mean.attrs.update(dict(long_name='LVMC Arithmetic Mean'))
    out.lvmc_stdv.attrs.update(dict(long_name='LVMC Standard Deviation'))
    out.time.encoding.update(dict(units='days since 1900-01-01',
                                  calendar='gregorian', dtype='i4'))
    for d in (out.lvmc_mean, out.lvmc_stdv):
        d.encoding.update(dict(
            shuffle=True, zlib=True, chunks=dict(x=400, y=400, time=6),
            # After compression, set fill to work around GSKY transparency bug
            _FillValue=-999, dtype='f4',
        ))
        d.attrs.update(dict(
            units='%', grid_mapping='sinusoidal',
            comment='Ratio of water to dry plant matter.  '
            'Mean of top 40 matches from observed to simulated reflectance.'
        ))

    # Save the file!
    if not os.path.isfile(out_file):
        # First time we've written this file
        out.to_netcdf(out_file)
    else:
        # otherwise, write next to final destination and move (atomic update)
        out.to_netcdf(out_file + '.new')
        shutil.move(out_file + '.new', out_file)
    # Make it visible via Thredds
    os.system('chmod a+rx ' + out_file)


def get_validated_args():

    def check_year(val):
        """Validate arg and transform glob pattern to file list."""
        assert re.match(r'\A20\d\d\Z', val), repr(val)
        return val

    def check_tile(val):
        """Validate that arg is tile string."""
        assert re.match(r'\Ah\d\dv\d\d\Z', val), repr(val)
        return val

    def change_output_path(val):
        """Validate that the directory exists """
        assert os.path.isdir(val), repr(val)
        return val

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-V', '--version', action='version', version=__version__)
    parser.add_argument(
        '--year', type=check_year,
        default=os.environ.get('FMC_YEAR', str(datetime.date.today().year)),
        help='four-digit year to process')
    parser.add_argument(
        '--tile', type=check_tile,
        default=os.environ.get('FMC_TILE', 'h31v10'),
        help='tile to process, "hXXvYY"')
    parser.add_argument(
        '--output-path', type=change_output_path,
        default=os.environ.get('FMC_PATH', '/g/data/ub8/au/FMC/LVMC/'),
        help='change output path')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_validated_args()
    print(args)
    main(args.year, args.tile, args.output_path)
