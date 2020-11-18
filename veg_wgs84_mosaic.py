import numpy as np
from glob import glob
import json
from datetime import datetime#, timedelta
import sys
from osgeo import gdal 
import netCDF4

wgs84_wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'

tile_size = 2400
au_tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11"]
mcd12q1_path = "/g/data/u39/public/data/modis/lpdaac-tiles-c6/MCD12Q1.006/{0}.01.01/MCD12Q1.A2018001.{1}.006.*.hdf"

def compose_mosaic(d):#, n_band, var_name, data_type):

    lat_max = -10.
    lat_min = -44.
    lon_max = 154.
    lon_min = 113.

    res = 0.005

    x_size = int((lon_max - lon_min)/res)
    y_size = int((lat_max - lat_min)/res)
    lats = np.linspace(lat_max, lat_min+res, num=y_size)
    lons = np.linspace(lon_min, lon_max-res, num=x_size)

    geot = [lon_min - res/2, res, 0., lat_max + res/2, 0., -1*res] #gdal geotransform indicate top left corner, not the coord of centre of top left pixel like netcdf

    src = gdal.GetDriverByName('MEM').Create('', tile_size, tile_size, 1, gdal.GDT_Byte,)

    dst = gdal.GetDriverByName('MEM').Create('', x_size, y_size, 1, gdal.GDT_Byte,)
    dst.SetGeoTransform(geot)
    dst.SetProjection(wgs84_wkt)

    for au_tile in au_tiles:
        modis_glob = mcd12q1_path.format(d.year, au_tile)
        modis_tiles = glob(modis_glob)


        if len(modis_tiles) != 1:
            exit(1)

        fname = modis_tiles[0]
        ds = gdal.Open('HDF4_EOS:EOS_GRID:"{}":MCD12Q1:LC_Type1'.format(fname))
        if ds is None:
            continue

        veg_mask = ds.GetRasterBand(1).ReadAsArray()
        print(np.unique(veg_mask))
        veg_mask[veg_mask == 1] = 3
        veg_mask[veg_mask == 2] = 3
        veg_mask[veg_mask == 3] = 3
        veg_mask[veg_mask == 4] = 3
        veg_mask[veg_mask == 5] = 3
        veg_mask[veg_mask == 6] = 2
        veg_mask[veg_mask == 7] = 2
        veg_mask[veg_mask == 8] = 3
        veg_mask[veg_mask == 9] = 3
        veg_mask[veg_mask == 10] = 1
        veg_mask[veg_mask == 11] = 0
        veg_mask[veg_mask == 12] = 1
        veg_mask[veg_mask == 13] = 0
        veg_mask[veg_mask == 14] = 0
        veg_mask[veg_mask == 15] = 0
        veg_mask[veg_mask == 16] = 0
        veg_mask[veg_mask == 17] = 0
        veg_mask[veg_mask == 254] = 0
        veg_mask[veg_mask == 255] = 0
        print(np.unique(veg_mask))

        src.GetRasterBand(1).WriteArray(veg_mask)

        src.SetGeoTransform(ds.GetGeoTransform())
        src.SetProjection(ds.GetProjection())
        err = gdal.ReprojectImage(src, dst, None, None, gdal.GRA_NearestNeighbour)

    return dst.ReadAsArray()

def pack_fmc_mosaic(date, veg_mask, dest):
    lat_max = -10.
    lat_min = -44.
    lon_max = 154.
    lon_min = 113.
    res = 0.005
    
    x_size = int((lon_max - lon_min)/res)
    y_size = int((lat_max - lat_min)/res)
    
    with netCDF4.Dataset(dest, 'w', format='NETCDF4_CLASSIC') as ds:
        with open('nc_metadata.json') as data_file:
            attrs = json.load(data_file)
            for key in attrs:
                setattr(ds, key, attrs[key])
        setattr(ds, "date_created", datetime.now().strftime("%Y%m%dT%H%M%S"))
        
        t_dim = ds.createDimension("time", 1)
        x_dim = ds.createDimension("longitude", veg_mask.shape[1])
        y_dim = ds.createDimension("latitude", veg_mask.shape[0])

        var = ds.createVariable("time", "f8", ("time",))
        var.units = "seconds since 1970-01-01 00:00:00.0"
        var.calendar = "standard"
        var.long_name = "Time, unix time-stamp"
        var.standard_name = "time"
        var[:] = netCDF4.date2num([date], units="seconds since 1970-01-01 00:00:00.0", calendar="standard")

        var = ds.createVariable("longitude", "f8", ("longitude",))
        var.units = "degrees"
        var.long_name = "longitude"
        var.standard_name = "longitude"
        var[:] = np.linspace(lon_min, lon_max-res, num=x_size)
        
        var = ds.createVariable("latitude", "f8", ("latitude",))
        var.units = "degrees"
        var.long_name = "latitude"
        var.standard_name = "latitude"
        var[:] = np.linspace(lat_max, lat_min+res, num=y_size)
        
        var = ds.createVariable("veg_mask", 'i1', ("time", "latitude", "longitude"), fill_value=0)
        var.long_name = "Vegetation Mask"
        var.units = 'Cat'
        var[:] = veg_mask[None,...]

#test
d = datetime(2018,1,1)
veg_mask = compose_mosaic(d)
pack_fmc_mosaic(d, veg_mask, "a.nc")
