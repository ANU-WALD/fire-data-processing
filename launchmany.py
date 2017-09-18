import os
import json

with open('tiles.json') as f:
    tiles = json.load(f)

for year in (2016, 2017):
    for tile, walltime in sorted(tiles.items()):
        fname = '/g/data/ub8/au/FMC/c6/LVMC_{}_{}.nc'.format(year, tile)
        if os.path.isfile(fname):
            print('Already done:', fname)
            continue
        print('Submitting job for', fname)
        os.system((
            'qsub -v "FMC_YEAR={year},FMC_TILE={tile}" '
            '-l walltime={hours}:00:00 -N {year}{tile}-FMC onetile.qsub'
        ).format(year=year, tile=tile, hours=walltime))
