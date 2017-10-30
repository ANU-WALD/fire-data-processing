import xarray as xr
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

# input files are downloaded from: ftp://mcst.ssaihq.com/pub/permanent/MCST/FM1_RSR_LUT_07-10-01/

continuous_lookup = pd.read_csv('continuous_lookup.csv')

def create_modis_data(filename):
    data_set = pd.read_fwf('MODIS_Data/' + filename,
                             comment='#',
                             skiprows=range(7),
                             names=['Band', 'Channel', 'Wavelength', 'RSR'])

    new_series = pd.Series(data_set['RSR'])
    new_series.index = data_set['Wavelength']
    new_series.groupby(['Wavelength']).mean()

    lookup = new_series.groupby(lambda i: 5 * ((i + 2.5) // 5)).mean()
    lookup /= lookup.sum()

    weighted_sum = 0
    for idx in lookup.index:
        weighted_sum += (lookup[idx] *  continuous_lookup[str(int(idx))])

    # rename on the basis that files are named 0X.amb.1pct.det
    # where X is the desired band number
    weighted_sum.rename('Band ' + filename[1])

    return weighted_sum

files = ['01.amb.1pct.det', '02.amb.1pct.det', '03.amb.1pct.det', '04.amb.1pct.det',
         '05.tv.1pct.det', '06.tv.1pct.det', '07.tv.1pct.det']

modis_lookup = continuous_lookup[['cab', 'chp', 'cm', 'cw', 'fcov', 'fmc', 'lai', 'landcover']]
for i, file in enumerate(files):
    modis_lookup['Band{}'.format(i)] = create_modis_data(file)

modis_lookup.to_csv('new_modis_lookup.csv')
