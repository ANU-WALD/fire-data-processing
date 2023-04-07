import numpy as np
import pandas as pd
import xarray as xr


data = np.random.rand(4, 3)
locs = ['IA', 'IL', 'IN']
times = pd.date_range('2000-01-01', periods=4)
foo = xr.DataArray(data, coords=[times, locs], dims=['time', 'space'])
foo.to_netcdf('test.nc')
print(foo)