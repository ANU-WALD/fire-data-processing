"""This script merges the currently-used lookup tables and renames columns."""

import pandas as pd

lut = pd.read_csv('original/LUT.TXT').set_index('ID')
lut['FMC'] = pd.read_csv('original/FMC.TXT').set_index('ID').FMC
lut['VEGTYPE'] = pd.read_csv('original/VEGTYPE.TXT').set_index('ID')\
    .FuelClass.replace({1: 'grass', 2: 'shrub', 3: 'forest'})

out = lut[['FMC', 'VEGTYPE', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']]

modis_band_map = {
    'B1': 'red_630_690',
    'B2': 'nir1_780_900',
    'B3': 'blue_450_520',
    'B4': 'green_530_610',
    'B5': 'nir2_1230_1250',
    'B6': 'swir1_1550_1750',
    'B7': 'swir2_2090_2350',
}
out.rename(columns=modis_band_map, inplace=True)
out.to_csv('merged_lookup.csv')
