import argparse
import datetime
import functools
import glob
import json
from osgeo import gdal
import netCDF4
import numpy as np
import os.path
import os

def tile_dates(tiles):
    dates = []

    for tile in tiles:
        dates.append(datetime.datetime.strptime(tile.split("/")[-2], "%Y.%m.%d"))

    return dates


def list_year_tiles(root_path, tile, year):
    year_tiles = []

    dirs = [x[0] for x in os.walk(root_path)]

    for d in dirs:
        d_name = d.split("/")[-1]
        if len(d_name.split(".")) == 3 and int(d_name.split(".")[0]) == year:
            files = [x[2] for x in os.walk(d)]
            for f in files[0]:
                if f.split(".")[2] == tile:
                    year_tiles.append(os.path.join(d, f))
    
    return sorted(year_tiles)


def pack(tiles, out_name):
    proj_wkt = None
    geot = None
        
    mean_stack = None
    stdv_stack = None
    mask_stack = None
    x_axis = None
    y_axis = None

    for file in sorted(tiles):
        with netCDF4.Dataset(file, 'r', format='NETCDF4') as src:
            if mean_stack is None:
                mean_stack = np.expand_dims(src["lfmc_mean"][:], axis=0)
                stdv_stack = np.expand_dims(src["lfmc_stdv"][:], axis=0)
                mask_stack = np.expand_dims(src["quality_mask"][:], axis=0)
                x_axis = src["x"][:]
                y_axis = src["y"][:]
                ds = gdal.Open('NETCDF:"{}":lfmc_mean'.format(file))
                proj_wkt = ds.GetProjection()
                geot = ds.GetGeoTransform()
            else:
                mean_stack = np.vstack((mean_stack, np.expand_dims(src["lfmc_mean"][:], axis=0)))
                stdv_stack = np.vstack((stdv_stack, np.expand_dims(src["lfmc_stdv"][:], axis=0)))
                mask_stack = np.vstack((mask_stack, np.expand_dims(src["quality_mask"][:], axis=0)))

    assert mean_stack is not None
    assert stdv_stack is not None
    assert mask_stack is not None
 
    timestamps = tile_dates(tiles)

    with netCDF4.Dataset(out_name, 'w', format='NETCDF4') as dest:
        with open('nc_metadata.json') as data_file:
            attrs = json.load(data_file)
            for key in attrs:
                setattr(dest, key, attrs[key])

        setattr(dest, "date_created", datetime.datetime.utcnow().isoformat())

        t_dim = dest.createDimension("time", len(timestamps))
        x_dim = dest.createDimension("x", mean_stack.shape[2])
        y_dim = dest.createDimension("y", mean_stack.shape[1])

        var = dest.createVariable("time", "f8", ("time",))
        var.units = "seconds since 1970-01-01 00:00:00.0"
        var.calendar = "standard"
        var.long_name = "Time, unix time-stamp"
        var.standard_name = "time"
        var[:] = netCDF4.date2num(timestamps, units="seconds since 1970-01-01 00:00:00.0", calendar="standard")

        var = dest.createVariable("x", "f8", ("x",))
        var.units = "m"
        var.long_name = "x coordinate of projection"
        var.standard_name = "projection_x_coordinate"
        var[:] = x_axis

        var = dest.createVariable("y", "f8", ("y",))
        var.units = "m"
        var.long_name = "y coordinate of projection"
        var.standard_name = "projection_y_coordinate"
        var[:] = y_axis

        var = dest.createVariable("lfmc_mean", 'f4', ("time", "y", "x"), fill_value=.0, zlib=True, chunksizes=(1, 240, 240))
        var.long_name = "LFMC Mean"
        var.units = '%'
        var.grid_mapping = "sinusoidal"
        var[:] = mean_stack

        var = dest.createVariable("lfmc_stdv", 'f4', ("time", "y", "x"), fill_value=.0, zlib=True, chunksizes=(1, 240, 240))
        var.long_name = "LFMC Standard Deviation"
        var.units = '%'
        var.grid_mapping = "sinusoidal"
        var[:] = stdv_stack
        
        var = dest.createVariable("quality_mask", 'i1', ("time", "y", "x"), fill_value=0, zlib=True, chunksizes=(1, 240, 240))
        var.long_name = "Quality Mask"
        var.units = 'Cat'
        var.grid_mapping = "sinusoidal"
        var[:] = mask_stack

        var = dest.createVariable("sinusoidal", 'S1', ())
        var.grid_mapping_name = "sinusoidal"
        var.false_easting = 0.0
        var.false_northing = 0.0
        var.longitude_of_central_meridian = 0.0
        var.longitude_of_prime_meridian = 0.0
        var.semi_major_axis = 6371007.181
        var.inverse_flattening = 0.0
        var.spatial_ref = proj_wkt
        var.GeoTransform = "{} {} {} {} {} {}".format(geot[0], geot[1], geot[2], geot[3], geot[4], geot[5])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modis Vegetation Analysis NetCDF aggregator.")
    parser.add_argument("-y", "--year", type=int, default=2017, required=False, help="Year to pack.")
    parser.add_argument("-t", "--tile_id", type=str, default="h29v12", required=False, help="Tile identifier.")
    parser.add_argument("-i", "--in_path", type=str, default="/g/data/fj4/scratch/2018", required=False, help="Input folder with FMC tiles.")
    parser.add_argument("-o", "--out_path", type=str, default="/g/data/fj4/scratch/2018", required=False, help="Output folder to write.")
    args = parser.parse_args()

    tiles = list_year_tiles(args.in_path, args.tile_id, args.year)
    pack(tiles, args.out_path + "/MCD43A4.A{}.{}.006.LFMC.nc".format(args.year, args.tile_id))
