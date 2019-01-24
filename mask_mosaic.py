import os.path
import numpy as np
import argparse
from glob import glob
from datetime import datetime
import netCDF4
import json
from osgeo import gdal 

mask_path = "/g/data/u39/public/data/modis/lpdaac-tiles-c6/MCD12Q1.006"
au_tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11"]
wgs84_wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
tile_size = 2400

def compose_mosaic(year, dst_path):
    print("{}/{}_latlon_mask.nc".format(dst_path, year))
    
    lat0 = -10.
    lat1 = -44.
    lon0 = 113.
    lon1 = 154.
    res = 0.005

    x_size = int((lon1 - lon0)/res)
    y_size = int((lat1 - lat0)/(-1*res))
    lats = np.linspace(lat0, lat1+res, num=y_size)
    lons = np.linspace(lon0, lon1-res, num=x_size)
    
    src = gdal.GetDriverByName('MEM').Create('', tile_size, tile_size, 1, gdal.GDT_Byte,)

    geot = [lon0, res, 0., lat0, 0., -1*res]
    dst = gdal.GetDriverByName('MEM').Create('', x_size, y_size, 1, gdal.GDT_Byte,)
    dst.GetRasterBand(1).WriteArray(np.zeros((y_size, x_size), dtype=np.uint8))
    dst.SetGeoTransform(geot)
    dst.SetProjection(wgs84_wkt)

    for au_tile in au_tiles:
        masks = glob("{}/{}.01.01/MCD12Q1.A{}001.{}.006.*.hdf".format(mask_path, year, year, au_tile))
        if len(masks) != 1:
            return None
        mask_tile = gdal.Open('HDF4_EOS:EOS_GRID:"{}":MCD12Q1:LC_Type1'.format(masks[0]))

        # Categories: 1=Grass 2=Shrub 3=Forest 0=No fuel
        veg_mask = mask_tile.ReadAsArray()
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
        print(np.unique(veg_mask, return_counts=True))

        src.GetRasterBand(1).WriteArray(veg_mask)

        src.SetGeoTransform(mask_tile.GetGeoTransform())
        src.SetProjection(mask_tile.GetProjection())
        err = gdal.ReprojectImage(src, dst, None, None, gdal.GRA_NearestNeighbour)
        print(err)
  
    with netCDF4.Dataset("{}/mask_{}.nc".format(dst_path, year), 'w', format='NETCDF4_CLASSIC') as ds:
        with open('nc_metadata.json') as data_file:
            attrs = json.load(data_file)
            for key in attrs:
                setattr(ds, key, attrs[key])
        setattr(ds, "date_created", datetime.now().strftime("%Y%m%dT%H%M%S"))
        
        x = np.linspace(lon0, lon1-res, num=x_size)
        y = np.linspace(lat0, lat1+res, num=y_size)
        t_dim = ds.createDimension("time", 1)
        x_dim = ds.createDimension("longitude", x.shape[0])
        y_dim = ds.createDimension("latitude", y.shape[0])

        var = ds.createVariable("time", "f8", ("time",))
        var.units = "seconds since 1970-01-01 00:00:00.0"
        var.calendar = "standard"
        var.long_name = "Time, unix time-stamp"
        var.standard_name = "time"
        var[:] = netCDF4.date2num([datetime(year, 1, 1, 0, 0)], units="seconds since 1970-01-01 00:00:00.0", calendar="standard")

        var = ds.createVariable("longitude", "f8", ("longitude",))
        var.units = "degrees"
        var.long_name = "longitude"
        var.standard_name = "longitude"
        var[:] = np.linspace(lon0, lon1-res, num=x_size)
        
        var = ds.createVariable("latitude", "f8", ("latitude",))
        var.units = "degrees"
        var.long_name = "latitude"
        var.standard_name = "latitude"
        var[:] = np.linspace(lat0, lat1+res, num=y_size)
        
        var = ds.createVariable("quality_mask", 'i1', ("time", "latitude", "longitude"), fill_value=0)
        var.long_name = "Vegetation Mask"
        var.units = 'Cat'
        var[:] = dst.ReadAsArray()[None,...]


    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Modis Vegetation Analysis argument parser""")
    parser.add_argument('-y', '--year', type=int, required=True, help="Year of data.")
    parser.add_argument('-dst', '--destination', required=True, type=str, help="Full path to destination.")
    args = parser.parse_args()

    print(args.year, args.destination)
    compose_mosaic(args.year, args.destination)

