import os
import argparse
from datetime import datetime
import xarray as xr
import numpy as np
import netCDF4


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-t', '--tile', help='Tile for computing the average hXXvXX', type=str, required=True)
    args = vars(parser.parse_args())

    mean = np.zeros((2400, 2400), dtype=np.float32)
    i = 0

    for root, dirs, files in os.walk("/g/data/ub8/au/FMC/2018"):
        for name in files:
            if name.endswith(".nc"):
                d = datetime.strptime(root.split("/")[-1], '%Y.%m.%d')
                if d >= datetime(2001, 1, 1) and d < datetime(2017, 1, 1):
                    fname_parts = name.split(".")
                    if fname_parts[2] == args["tile"]:
                        tile_path = os.path.join(root, name)
                        print(tile_path)
                        mean += xr.open_dataset(tile_path).lfmc_mean[:].data
                        print(np.nanmax(mean))
                        i += 1

    print(mean, i)

    with netCDF4.Dataset("/g/data/ub8/au/FMC/2018/mean_2001_2016_{}.nc".format(args["tile"]), 'w', format='NETCDF4_CLASSIC') as dest:
        setattr(dest, "date_created", datetime.now().strftime("%Y%m%dT%H%M%S"))
       
        dest.createDimension("x", 2400)
 
        var = dest.createVariable("x", "f8", ("x",))
        var.units = "m"
        var.long_name = "x coordinate of projection"
        var.standard_name = "projection_x_coordinate"
        var[:] = np.arange(2400)
        
        dest.createDimension("y", 2400)
        
        var = dest.createVariable("y", "f8", ("y",))
        var.units = "m"
        var.long_name = "y coordinate of projection"
        var.standard_name = "projection_y_coordinate"
        var[:] = np.arange(2400)
        
        var = dest.createVariable("lfmc_mean", 'f4', ("y", "x"), fill_value=.0)
        var.long_name = "LFMC Arithmetic Mean"
        var.units = '%'
        var[:] = mean / i
