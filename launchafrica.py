import os
import datetime

tiles = {'h19v11': 24, 'h20v11': 36, 'h21v11': 8, 'h19v12': 6, 'h20v12': 10}
path = '/g/data/xc0/project/SouthAfrica_CSIR/'

for tile, walltime in sorted(tiles.items(), key=lambda k: (k[1], k[0])):
    for year in range(2001, datetime.date.today().year + 1):
        fname = path + 'LVMC_{}_{}.nc'.format(year, tile)
        if os.path.isfile(fname):
            print('Already done:', fname)
            continue
        print('Submitting job for', fname)
        os.system((
            'qsub -v "FMC_YEAR={year},FMC_TILE={tile},FMC_PATH={path}" '
            '-l walltime={hours}:00:00 -N {year}{tile}-FMC onetile.qsub'
        ).format(year=year, tile=tile, hours=walltime, path=path))
