import os
import json
import datetime

with open('tiles.json') as f:
    tiles = json.load(f)

for tile, walltime in sorted(tiles.items(), key=lambda k: (k[1], k[0])):
    for year in range(2001, datetime.date.today().year + 1):
        fname = '/g/data/ub8/au/FMC/c6/LVMC_{}_{}.nc'.format(year, tile)
        if os.path.isfile(fname):
            print('Already done:', fname)
            continue
        print('Submitting job for', fname)
        os.system((
            'qsub -v "FMC_YEAR={year},FMC_TILE={tile}" '
            '-l walltime={hours}:00:00 -N {year}{tile}-FMC onetile.qsub'
        ).format(year=year, tile=tile, hours=walltime))
