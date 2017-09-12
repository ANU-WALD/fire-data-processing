
# coding: utf-8
from __future__ import print_function

import os
import re
from os import path
import datetime as dt
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor


import numpy as np
import pandas as pd
import xarray as xr


cache = '/g/data/xc0/user/HatfieldDodds/c6.txt'

tiles = ['h27v11', 'h27v12', 'h28v11', 'h28v12', 'h28v13', 'h29v10', 'h29v11',  'h29v12',
         'h29v13', 'h30v10', 'h30v11', 'h30v12', 'h31v10', 'h31v11', 'h31v12', 'h32v10', 'h32v11']

out_dir = '/g/data/xc0/project/FMC_Australia/MCD43A4-collection-six/'  # '/g/data1/xc0/user/HatfieldDodds/c6/'


if not path.isfile(cache):
    files = set()
    base = '/g/data/u39/public/data/modis/lpdaac-tiles-c6/MCD43A4.006/'
    for d in os.listdir(base):
        pth = base + d + '/'
        for f in os.listdir(pth):
            if f.endswith('.hdf') and any(t in f for t in tiles):
                files.add(pth + f)
    files = sorted(files)
    with open(cache, 'w') as f:
        f.write('\n'.join(files) + '\n')
else:
    with open(cache) as f:
        files = [l.strip() for l in f.readlines()]


groups = defaultdict(list)
pattern = re.compile(r'MCD43A4.A(?P<year>\d{4})(?P<day>\d{3}).(?P<tile>h\d\dv\d\d).006.\d+.hdf')
for f in files:
    year, day, tile = pattern.match(path.basename(f)).groups()
    date = dt.date(int(year), 1, 1) + dt.timedelta(days=int(day) - 1)
    groups[(year, tile)].append((date, f))
groups = {k: sorted(v) for k, v in groups.items()}


def make_one(key):
    
    dates, files = zip(*groups[key])
    dates = pd.to_datetime(dates)
    dates.name = 'time'
    
    ds = xr.concat([xr.open_dataset(fname, chunks=800) for fname in files], dates)
    out = xr.Dataset()

    for i in range(1, 8):
        band = str(i)
        out['band' + band] = ds['Nadir_Reflectance_Band' + band].astype('f4')\
            .where(ds['BRDF_Albedo_Band_Mandatory_Quality_Band' + band] == 1)

    out.rename({'YDim:MOD_Grid_BRDF': 'y', 'XDim:MOD_Grid_BRDF': 'x'}, inplace=True)
    out.time.encoding.update(dict(units='days since 1900-01-01', calendar='gregorian', dtype='i4'))
    out.encoding.update(dict(chunks=dict(x=800, y=800, time=6), shuffle=True, zlib=True))

    return out
    
    
def write_one(key):
    fname = out_dir + 'MCD43A4.A%s.%s.006.nc' % key  # year, tile
    marker = fname + '.inprogress'
    if os.path.isfile(fname) and not os.path.isfile(marker):
	print('{} already done'.format(key))
        return
    with open(marker, 'w') as f:
        pass
    make_one(key).to_netcdf(fname)
    os.remove(marker)


def try_write(key):
    for _ in range(10):
        try:
            write_one(key)
            print('{} done'.format(key))
            break
        except IOError:
	    print('{} failed'.format(key))


if __name__ == '__main__':
    with ProcessPoolExecutor() as pool:
        pool.map(try_write, reversed(sorted(groups)))

