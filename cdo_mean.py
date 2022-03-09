import os
import uuid 
import argparse

fmc_tile = "/g/data/ub8/au/FMC/c6/fmc_c6_{}_{}.nc"
mean_tile = "/g/data/ub8/au/FMC/c6/mean_2001_2021_{}.nc"
au_tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""FMC time average calculator""")
    parser.add_argument('-tmp', '--tmp', required=True, type=str, help="Full path to tmp directory.")
    args = parser.parse_args()

    for tile_id in au_tiles:
        fmc_tiles = [fmc_tile.format(year, tile_id) for year in range(2001,2022)]

        tmp_file = os.path.join(args.tmp, "{}.nc".format(uuid.uuid4().hex))
        dst_file = mean_tile.format(tile_id)
        os.system("cdo -V -select,name=lfmc_median {} {}".format(' '.join(fmc_tiles), tmp_file))
        os.system("cdo -V -timmean -selvar,lfmc_median {} {}".format(tmp_file, dst_file))
        os.remove(tmp_file)
