import os
import argparse
from datetime import datetime

au_tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-y', '--year', help='Year for the modis tiles', type=int, required=True)
    args = vars(parser.parse_args())

    for root, dirs, files in os.walk("/g/data/u39/public/data/modis/lpdaac-tiles-c6/MCD43A4.006"):
        for name in files:
            if name.endswith(".hdf"):
                d = datetime.strptime(root.split("/")[-1], '%Y.%m.%d')
                if d >= datetime(args["year"], 1, 1) and d < datetime(args["year"]+1, 1, 1):
                    fname_parts = name.split(".")
                    if fname_parts[2] in au_tiles:
                        print("/g/data1/xc0/software/conda-envs/rs3/bin/python /home/603/pl5189/github/fire-data-processing/main.py", os.path.join(root, name), "/g/data/ub8/au/FMC/2018/{}".format(root.split("/")[-1]))
