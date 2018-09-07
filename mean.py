import os
import argparse
from datetime import datetime
import xarray as xr

src_path = "/g/data/fj4/scratch/2018"

def get_file_paths(year_start, year_end, tile):
    paths = []
    for root, dirs, files in os.walk(src_path):
        for name in files:
            if name.startswith("MCD") and name.endswith(".nc") and name.split(".")[2] == tile:
                year = int(name.split(".")[1][1:])
                if year >= year_start and year < year_end:
                    paths.append(os.path.join(root, name))
    return sorted(paths)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-t', '--tile', help='Tile for computing the average hXXvXX', type=str, required=True)
    args = vars(parser.parse_args())

    paths = get_file_paths(2001, 2017, args["tile"])
    xr.open_mfdataset(paths).lfmc_mean.mean(dim='time').to_netcdf(os.path.join(src_path, "mean_2001_2016_{}.nc".format(args["tile"])))
