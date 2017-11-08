import os
import re
import json
import datetime
import argparse

import numpy as np

import onetile

__version__ = '0.1.0'

def main(tiles_list):
    for tile in tiles_list:
        masks = onetile.get_masks(2017, tile)
        elements = np.sum(masks['forest'] | masks['shrub'] | masks['grass'])
        walltime = int(np.ceil(36 * elements / 2400 ** 2))
        for year in range(2001, datetime.date.today().year + 1):
            fname = '/g/data/ub8/au/FMC/LVMC/LVMC_{}_{}.nc'.format(year, tile)
            if os.path.isfile(fname):
                print('Already done:', fname)
                continue
            print('Submitting job for', fname)
            os.system((
                'qsub -v "FMC_YEAR={year},FMC_TILE={tile}" '
                '-l walltime={hours}:00:00 -N {year}{tile}-FMC onetile.qsub'
            ).format(year=year, tile=tile, hours=walltime))


def cli_get_args():
    shortcuts = {
                "australia":
                "h28v13,h29v11,h28v12,h29v10,h29v12,h32v10,h27v11, \
                h31v11,h32v11,h30v11,h30v10,h27v12,h30v12,h31v12, \
                h31v10,h29v13,h28v11",

                "south_africa": #only capitalise first letter to pass
                "h19v11,h20v11,h21v11,h19v12,h20v12"
                }

    def check_valid_location(arg):
        arg = arg.lower()

        if arg in shortcuts.keys():
            print('Used the shortcut:', arg)
            arg = shortcuts[arg]

        generated_list = [coord.strip() for coord in arg.split(',')]

        for item in generated_list:
            regexp = re.fullmatch(r'h(\d\d?)v(\d\d?)', item)
            assert regexp, item
            assert int(regexp.group(1)) in range(36), item
            assert int(regexp.group(2)) in range(18), item

        return generated_list

    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '--version',
                        action='version',
                        version=__version__)
    parser.add_argument('--tiles',
                        metavar='<Australia, South_Africa, CSV>',
                        help='Location as comma separated tiles or shortcut',
                        default='australia',
                        type=check_valid_location)

    return parser.parse_args()


if __name__ == '__main__':
    get_args = cli_get_args()
    print(get_args.tiles)
    #main(get_args.tiles)
