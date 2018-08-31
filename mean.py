import os
import argparse
from datetime import datetime
import xarray as xr

src_path = "/g/data/ub8/au/FMC/2018"

def get_file_paths(year_start, year_end):
    paths = []
    for root, dirs, files in os.walk(src_path):
        for name in files:
            if name.startswith("MCD") and name.endswith(".nc"):
                d = datetime.strptime(root.split("/")[-1], '%Y.%m.%d')
                if d >= datetime(year_start, 1, 1) and d < datetime(year_end, 1, 1):
                    fname_parts = name.split(".")
                    if fname_parts[2] == args["tile"]:
                        tile_path = os.path.join(root, name)
                        paths.append(tile_path)
    return paths

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-t', '--tile', help='Tile for computing the average hXXvXX', type=str, required=True)
    args = vars(parser.parse_args())

    tile = args["tile"]

    paths = get_file_paths(2001, 2017)
    xr.open_mfdataset(paths).mean(dim='time').to_netcdf(src_path + "test.nc")
