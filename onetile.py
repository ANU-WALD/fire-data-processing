"""
Script to create one tile-year of LFMC data, from the original MODIS products.

It's also a best-possible port of equations developed for MODIS C5 to C6 data;
we plan to fully upgrade in future but that will require revalidation.

"""

import os
import re
import json
import shutil
import typing as t
import argparse
import datetime

import numpy as np
import pandas as pd
import xarray as xr

import modis

__version__ = '0.3.0'

bands_to_use = {'MODIS': ['red_630_690', 'nir1_780_900', 'green_530_610',
                          'swir1_1550_1750', 'swir2_2090_2350', 'ndii'],
                'SPOT6': ['band_0_blue', 'band_1_green', 'band_2_red',
                          'band_3_nir'],
                'SPOT7': ['band_0_blue', 'band_1_green', 'band_2_red',
                          'band_3_nir'],
                }

# TODO: make return type annotation more precise
functor_cache = {}  # type: t.Dict[t.Tuple[str, str], t.Callable]


def get_functor(veg_type: str, satellite: str) -> t.Callable:
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

    # TODO: more precise types may be possible via mypy/numpy extension?
    def get_top_n(mb: np.ndarray, vmat: np.ndarray=vmat,
                  vsmat: np.ndarray=vsmat, fmc: np.ndarray=fmc
                  ) -> t.Tuple[float, float]:
        spectral_angle = np.arccos(
            np.einsum('ij,j->i', vmat, mb) /
            (np.sqrt(np.einsum('i,i->', mb, mb)) * vsmat)
        )
        top_values = fmc[np.argpartition(spectral_angle, 40)[:40]]
        return np.median(top_values, axis=-1), top_values.std(axis=-1)

    functor_cache[(veg_type, satellite)] = get_top_n
    return get_top_n


def get_fmc(dataset: xr.Dataset,
            masks: t.Optional[t.Dict[str, xr.DataArray]]=None,
            satellite: str='MODIS') -> xr.Dataset:
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


def save_for_thredds(ds: xr.Dataset, fname: str) -> None:
    # Update time encoding, because Thredds can't handle int64 data.
    ds.time.encoding.update(dict(
        units='days since 1900-01-01', calendar='gregorian', dtype='i4'))
    # Save the file!
    if not os.path.isfile(fname):
        # First time we've written this file
        ds.to_netcdf(fname)
    else:
        # otherwise, write next to final destination and move (atomic update)
        ds.to_netcdf(fname + '.new')
        shutil.move(fname + '.new', fname)
    # Make it visible via Thredds
    os.chmod(fname, 0o755)


def main(year: int, tile: str, output_path: str) -> None:
    out_file = os.path.join(output_path, 'LVMC_{}_{}.nc'.format(year, tile))
    # Get the landcover masks
    masks = modis.get_masks(year, tile)
    # Get the main dataset - demo is one tile for a year
    ds = modis.get_reflectance(year, tile)

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
        modis.add_tile_coords(tile, new_data)
        out = xr.merge([existing, new_data])

    with open('nc_metadata.json') as f:
        json_attrs = json.load(f)
    if 'x' not in out.coords or 'y' not in out.coords:
        modis.add_tile_coords(tile, out)

    # Add metadata to the resulting file
    out.attrs.update(json_attrs)

    out.lvmc_mean.attrs.update(dict(long_name='LVMC Arithmetic Mean'))
    out.lvmc_stdv.attrs.update(dict(long_name='LVMC Standard Deviation'))
    for d in (out.lvmc_mean, out.lvmc_stdv):
        d.encoding.update(dict(
            shuffle=True, zlib=True, chunks=dict(x=400, y=400, time=6),
        ))
        d.attrs.update(dict(
            units='%', grid_mapping='sinusoidal',
            comment='Ratio of water to dry plant matter.  '
            'Mean of top 40 matches from observed to simulated reflectance.'
        ))

    save_for_thredds(out, out_file)


def valid_tile(val: str) -> str:
    """Validate that arg is tile string."""
    assert re.match(r'\Ah\d\dv\d\d\Z', val), repr(val)
    return val


def get_arg_parser(default_subdir: str='') -> argparse.ArgumentParser:

    def valid_year(val: str) -> str:
        """Validate arg and transform glob pattern to file list."""
        assert re.match(r'\A20\d\d\Z', val), repr(val)
        return val

    def valid_output_path(val: str) -> str:
        """Validate that the directory exists """
        assert os.path.isdir(val), repr(val)
        return val

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-V', '--version', action='version', version=__version__)
    parser.add_argument(
        '--year', type=valid_year,
        default=os.environ.get('FMC_YEAR', str(datetime.date.today().year)),
        help='four-digit year to process')
    parser.add_argument(
        '--output-path', type=valid_output_path,
        default=os.environ.get('FMC_PATH',
                               '/g/data/ub8/au/FMC/' + default_subdir),
        help='change output path')
    return parser


if __name__ == '__main__':
    parser = get_arg_parser(default_subdir='LVMC')
    parser.add_argument(
        '--tile', type=valid_tile,
        default=os.environ.get('FMC_TILE', 'h31v10'),
        help='tile to process, "hXXvYY"')
    args = parser.parse_args()
    print(args)
    main(args.year, args.tile, args.output_path)
