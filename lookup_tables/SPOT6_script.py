
# coding: utf-8

# In[111]:


import pandas as pd

which_satellite = 'SPOT6'

continuous_lookup = pd.read_csv('continuous_lookup.csv')
data_set = pd.read_excel('SPOT_sensitivity.xlsx', sheetname=which_satellite,
                         index_col=0)
modis_lookup = pd.DataFrame(continuous_lookup[
                ['cab', 'chp', 'cm', 'cw', 'fcov', 'fmc', 'lai', 'landcover']])

data_set.rename(columns={'B0(Blue)': 'band_0_blue',
                         'B1(Green)': 'band_1_green',
                         'B2(Red)': 'band_2_red', 'B3(NIR)': 'band_3_nir'},
                inplace=True)
data_set.index.name = 'Wavelength'
data_set.index *= 1000
data_set.drop('PAN', axis=1, inplace=True)
data_set.T

lookup = data_set.groupby(lambda i: 5 * ((i + 2.5) // 5)).mean()
lookup /= lookup.sum()

for band in lookup.columns:
    tmp = 0
    for idx in lookup.index:
        tmp += (lookup[band][idx] * continuous_lookup[str(int(idx))])
    modis_lookup[band] = tmp


# In[113]:


modis_lookup.to_csv(which_satellite + '_lookup.csv')
