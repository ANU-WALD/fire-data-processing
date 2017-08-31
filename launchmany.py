import os

tiles = ('h27v11 h27v12 h28v11 h28v12 h28v13 h29v10 h29v11 h29v12 h29v13 '
         'h30v10 h30v11 h30v12 h30v13 h31v10 h31v11 h31v12 h32v10 h32v11').split()

for year in (2016, 2017):
    for tile in tiles:
        os.system('qsub -v "FMC_YEAR={},FMC_TILE={}" onetile.qsub'.format(year, tile))
