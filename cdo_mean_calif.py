import os
import uuid 
import argparse

fmc_tile = "/g/data/ub8/au/FMC/c6/fmc_c6_{}_{}.nc"
mean_tile = "/g/data/ub8/au/FMC/c6/mean_2001_2016_{}.nc"
au_tiles = ["h08v05"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""FMC time average calculator""")
    parser.add_argument('-tmp', '--tmp', required=True, type=str, help="Full path to tmp directory.")
    args = parser.parse_args()

    for tile_id in au_tiles:
        print(tile_id)
        fmc_tiles = [fmc_tile.format(year, tile_id) for year in range(2001,2017)]

        tmp_file = os.path.join(args.tmp, "{}.nc".format(uuid.uuid4().hex))
        dst_file = mean_tile.format(tile_id)
        os.system("cdo -V -select,name=lfmc_mean {} {}".format(' '.join(fmc_tiles), tmp_file))
        os.system("cdo -V -timmean -selvar,lfmc_mean {} {}".format(tmp_file, dst_file))
        os.remove(tmp_file)
