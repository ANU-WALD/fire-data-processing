import os
import json

with open('tiles.json') as f:
    tiles = sorted(json.load(f))

for tile in tiles:
    cmd = 'qsub -v "FMC_TILE={tile}" -N {tile}-flammability.qsub'.format(tile=tile)
    print(cmd)
    os.system(cmd)
