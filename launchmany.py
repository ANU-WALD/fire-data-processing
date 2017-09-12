import os
import json

with open('tiles.json') as f:
    tiles = json.load(f)

for year in (2016, 2017):
    for tile in tiles:
        fname = '/g/data/ub8/au/FMC/c6/LVMC_{}_{}.nc'.format(year, tile)
        if os.path.isfile(fname):
            print('Already done:', fname)
            continue
        print('Submitting job for', fname)
        os.system('qsub -v "FMC_YEAR={},FMC_TILE={}" onetile.qsub'.format(year, tile))
