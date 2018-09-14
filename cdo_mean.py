import os
import uuid 

fmc_tile = "/g/data/fj4/scratch/2018/MCD43A4.A{}.{}.006.LFMC.nc"

au_tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11"]

for tile_id in au_tiles:
    fmc_tiles = [fmc_tile.format(year, tile_id) for year in range(2001,2017)]

    tmp_file = "/g/data/fj4/scratch/" + uuid.uuid4().hex + ".nc"
    os.system("cdo -V -select,name=lfmc_mean {} {}".format(' '.join(fmc_tiles), tmp_file))
    os.system("cdo -V -timmean -selvar,lfmc_mean {} mean_2001_2016_{}.nc".format(tmp_file, tile_id))
    os.remove(tmp_file)

#
