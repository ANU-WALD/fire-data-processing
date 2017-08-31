import json
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import xarray as xr


in_file = '/g/data1/xc0/project/FMC_Australia/MCD43A4-collection-six/MCD43A4.A2017.h31v11.006.nc'
lc_file = '/g/data/xc0/user/HatfieldDodds/FMC/landcover.2013.h31v11.nc'

with open('modis_prods/nc_metadata.json') as f:
    json_attrs = json.load(f)

modis_band_map = {
    'band1': 'red_630_690',
    'band2': 'nir1_780_900',
    'band3': 'blue_450_520',
    'band4': 'green_530_610',
    'band5': 'nir2_1230_1250',
    'band6': 'swir1_1550_1750',
    'band7': 'swir2_2090_2350',
}

bands_to_use = ['red_630_690', 'nir1_780_900', 'green_530_610',
                'swir1_1550_1750', 'swir2_2090_2350', 'ndii']


# Get the main dataset - demo is one tile for a year
ds = xr.open_dataset(in_file, chunks=dict(time=1, y=800, x=800))
ds.rename(modis_band_map, inplace=True)
ds['ndvi_ok_mask'] = 0.15 < (ds.nir1_780_900 - ds.red_630_690) / (ds.nir1_780_900 + ds.red_630_690)
ds['ndii'] = (ds.nir1_780_900 - ds.swir1_1550_1750) / (ds.nir1_780_900 + ds.swir1_1550_1750)

# Get the landcover masks
lc = xr.open_dataarray(lc_file)
shrub_mask = sum((lc == i) for i in (6, 7)).astype(bool)
grass_mask = sum((lc == i) for i in (10, 12)).astype(bool)
forest_mask = sum((lc == i) for i in (1, 2, 3, 4, 5, 8, 9)).astype(bool)

# Get the lookup table
merged_lookup = pd.read_csv('lookup_tables/merged_lookup.csv', index_col='ID')
merged_lookup['ndii'] = ((merged_lookup.nir1_780_900 - merged_lookup.swir1_1550_1750) /
                         (merged_lookup.nir1_780_900 + merged_lookup.swir1_1550_1750))


@lru_cache()
def get_functor(veg_type, n=40):
    """Returns a function to get the mean and stdev of LFMC for the top n values.
    
    Note that the function object is jitted with Numba if possible, and
    therefore cached to maximise the benefit of jitting and avoid loading
    the vmat and smat tables more than once.
    """
    table = merged_lookup.where(merged_lookup.VEGTYPE == veg_type)
    vmat = table[bands_to_use].values
    vsmat = np.sqrt((vmat ** 2).sum(axis=1))
    
    def get_top_n(mb, top_n=n, vmat=vmat, vsmat=vsmat, fmc=table.FMC.values):
        spectral_angle = np.arccos(
            np.einsum('ij,j->i', vmat, mb) /
            (np.sqrt(np.einsum('i,i->', mb, mb)) * vsmat)
        )
        top_values = fmc[np.argpartition(spectral_angle, top_n)[:top_n]]
        return top_values.mean(axis=-1), top_values.std(axis=-1)
    
    return get_top_n


def get_fmc(dataset):
    """Get the mean and stdev of LFMC for the given Xarray dataset (one time-step)."""
    bands = xr.concat([dataset[b] for b in bands_to_use], dim='band')
    ok = np.logical_and(dataset.ndvi_ok_mask, bands.notnull().all(dim='band'))
    
    out = np.full((2,) + ok.shape, np.nan, dtype='float32')
    
    for kind, mask in [('shrub', shrub_mask), ('forest', forest_mask), ('grass', grass_mask)]:
        cond = np.logical_and(ok, mask[:bands.y.size, :bands.x.size]).values
        vals = bands.values[:, cond]
        if vals.size:
            # Only calculate for and assign to the unmasked values
            out[:,cond] = np.apply_along_axis(get_functor(kind), 0, vals)
    
    data_vars = dict(lfmc_mean=(('y', 'x'), out[0]), 
                     lfmc_stdv=(('y', 'x'), out[1]))
    return xr.Dataset(data_vars=data_vars, coords=dataset.coords)


def add_sinusoidal_var(dataset):
    if u'sinusoidal' in dataset.variables:
        return
    with open('sinusoidal.json') as f:
        attrs = json.load(f)
    attrs['GeoTransform'] = ' '.join(map(str, [
        # Affine matrix - start/step/rotation, start/rotation/step - in 1D
        ds.x[0], (ds.x[-1] - ds.x[0]) / ds.x.size, 0,
        ds.y[0], 0, (ds.y[-1] - ds.y[0]) / ds.y.size
    ]))
    dataset['sinusoidal'] = xr.DataArray(np.zeros((), 'S1'), attrs=attrs)

# Do the expensive bit
with ThreadPoolExecutor(28) as pool:
    slices = list(pool.map(lambda t: get_fmc(ds.sel(time=t)), ds.time))
out = xr.concat(slices, dim='time')

# Ugly hack because PyNIO dropped coords; add them in from another MODIS dataset
coord_ds = xr.open_dataset('/g/data/ub8/au/FMC/sinusoidal/MCD43A4.2001.h31v11.005.2007077085626_LFMC.nc')
out['x'] = coord_ds.x
out['y'] = coord_ds.y

# Add metadata to the resulting file
out.time.encoding.update(dict(units='days since 1900-01-01', calendar='gregorian', dtype='i4'))
out.encoding.update(dict(shuffle=True, zlib=True, chunks=dict(x=400, y=400, time=6)))
out.attrs.update(json_attrs)
add_sinusoidal_var(out)
var_attrs = dict(
    units='%', grid_mapping='sinusoidal',
    comment='Ratio of water to dry plant matter.  '
    'Mean of top 40 matches from observed to simulated reflectance.'
)
out.lfmc_mean.attrs.update(dict(long_name='LFMC Arithmetic Mean', **var_attrs))
out.lfmc_stdv.attrs.update(dict(long_name='LFMC Standard Deviation', **var_attrs))

# Save the file!
out.to_netcdf('/g/data/xc0/user/HatfieldDodds/LFMC_new_demo_test.nc')
out
