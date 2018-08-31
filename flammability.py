import datetime
import numpy as np
import xarray as xr

def get_fmc_path(tile, d):
    return "/g/data/ub8/au/FMC/2018/{0}/MCD43A4.A{1}{2:03d}.{3}.006.LFMC.nc".format(d.strftime("%Y.%m.%d"), d.year, d.timetuple().tm_yday, tile)

def get_long_mean_path(tile):
    return "/g/data/ub8/au/FMC/2018/mean_2001_2016_{}.nc".format(tile)

if __name__ == "__main__":
    t = datetime.datetime(2018, 7 , 12)
    tile = "h29v11"

    tm1 = t - datetime.timedelta(days=4)
    tm2 = t - datetime.timedelta(days=8)

    tm1_path = get_fmc_path(tile, tm1)
    tm2_path = get_fmc_path(tile, tm2)

    mean_tm1 = xr.open_dataset(tm1_path).lfmc_mean[:].data
    mean_tm2 = xr.open_dataset(tm2_path).lfmc_mean[:].data

    long_mean_path = get_long_mean_path(tile)
    long_mean = xr.open_dataset(long_mean_path).lfmc_mean[:].data

    print(mean_tm1, long_mean)
    print(long_mean.shape, np.count_nonzero(~np.isnan(long_mean)))



