import os
import argparse
from datetime import datetime
import xarray as xr
import numpy as np

mcd43_root = "/g/data/u39/public/data/modis/lpdaac-tiles-c6/MCD43A4.006"
fmc_root = "/g/data/fj4/scratch/2018"
fmc_stack_name = "MCD43A4.A{}.{}.006.LFMC.nc"

def get_fmc_stack_dates(year, tile):
    path = os.path.join(fmc_root, fmc_stack_name.format(year, tile))
    if os.path.isfile(path):
        ds = xr.open_dataset(path)
        return ds.time.data
        
    return None

def get_mcd43_dates(year, tile):
    paths = []
    for root, dirs, files in os.walk(mcd43_root):
        tile_dir = root.split("/")[-1]
        date_parts = tile_dir.split(".")
        if len(date_parts) != 3:
            continue
        y = int(date_parts[0])
        if y == year:
            for f in files:
                f_parts = f.split(".")
                if f.endswith(".hdf") and len(f_parts) == 6 and f_parts[2] == tile:
                    paths.append(datetime.strptime(tile_dir, "%Y.%m.%d"))

    return np.sort(np.array(paths, dtype=np.datetime64))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-y', '--year', help='Year to update file', type=int, required=True)
    parser.add_argument('-t', '--tile', help='Tile for computing the average hXXvXX', type=str, required=True)
    args = vars(parser.parse_args())

    fmc_dates = get_fmc_stack_dates(args["year"], args["tile"])
    mcd43_dates = get_mcd43_dates(args["year"], args["tile"])
    missing_dates = np.setdiff1d(mcd43_dates, fmc_dates)

    print(missing_dates)
