from datetime import datetime
from matplotlib import pyplot as plt
import numpy as np
from osgeo import gdal, osr

au_tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11"]
wgs84_wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'

lat0 = -10.
lat1 = -44.
lon0 = 113.
lon1 = 154.
res = 0.005

x_size = int((lon1 - lon0)/res)
y_size = int((lat1 - lat0)/(-1*res))
lats = np.linspace(lat0, lat1+res, num=y_size)
lons = np.linspace(lon0, lon1-res, num=x_size)

def get_lfmc_mosaic(param, d):

    dst = gdal.GetDriverByName('MEM').Create('', x_size, y_size,)
    geot = [lon0, res, 0., lat0, 0., -1*res]
    dst.SetGeoTransform(geot)
    dst.SetProjection(wgs84_wkt)

    for au_tile in au_tiles:
        src = gdal.Open('NETCDF:"/g/data/ub8/au/FMC/2018/{0}/MCD43A4.A{1}{2:03d}.{3}.006.LFMC.nc":{4}'.format(d.strftime('%Y.%m.%d'), d.year, d.timetuple().tm_yday, au_tile, param))
        print(src)

        gdal.ReprojectImage(src, dst, None, None, gdal.GRA_NearestNeighbour)

    return dst.ReadAsArray()

plt.imsave("out.png", get_lfmc_mosaic("lfmc_mean", datetime(2018, 8, 17)))

