import os
import json
import datetime

with open('tiles.json') as f:
    tiles = sorted(json.load(f))

cmd = 'qsub -v "FMC_YEAR={y},FMC_TILE={t}" -N {t}-{y} flammability.qsub'

for tile in tiles:
    for year in range(2001, datetime.date.today().year + 1):
        fname = '/g/data/ub8/au/FMC/c6/Flammability_{}_{}.nc'.format(year, tile)
        if os.path.isfile(fname):
            print('Already done:', fname)
            continue
        print('Submitting job for', fname)
        os.system(cmd.format(y=year ,t=tile))
