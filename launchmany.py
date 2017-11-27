#!/usr/bin/env python

import os
import re
import datetime
import argparse

import numpy as np
import xarray as xr

import onetile

__version__ = '0.1.0'

def main(tiles_list, path, start_year):
    for tile in tiles_list:
        masks = onetile.get_masks(2017, tile)
        elements = np.sum(masks['forest'] | masks['shrub'] | masks['grass'])
        walltime = int(np.ceil(9 * elements / 2400. ** 2)) + 2

        print('Calculated walltime for tile:', tile, '=', walltime)
        for year in range(start_year, datetime.date.today().year + 1):

            fname = os.path.join(path, 'LVMC_{}_{}.nc'.format(year, tile))
            if os.path.isfile(fname):
                if year == datetime.date.today().year:
                    reflectance = onetile.get_reflectance(year, tile)
                    output_dataset = xr.open_dataset(fname)
                    reflectance_times = reflectance.time[:len(output_dataset.time)]
                    new_obs = len(reflectance.time) - len(output_dataset.time)
                    assert np.all(reflectance_times == output_dataset.time)
                    if not new_obs:
                        print('Already done:', fname)
                        continue
                    walltime = int(np.ceil(9 * elements * (new_obs / 90)
                                           / 2400. ** 2 + 0.5))
                    print('Update walltime: {}h for {} steps'
                          .format(walltime, new_obs))
                else:
                    print('Already done:', fname)
                    continue
            print('Submitting job for', fname)
            os.system((
                'qsub -v "FMC_YEAR={year},FMC_TILE={tile},FMC_PATH={path}" '
                '-l walltime={hours}:00:00 -N {year}{tile}-FMC onetile.qsub'
            ).format(year=year, tile=tile, hours=walltime, path=path))


def cli_get_args():
    shortcuts = dict(
        australia=('h28v13,h29v11,h28v12,h29v10,h29v12,h32v10,h27v11,'
                   'h31v11,h32v11,h30v11,h30v10,h27v12,h30v12,h31v12,'
                   'h31v10,h29v13,h28v11'),
        south_africa='h19v11,h20v11,h21v11,h19v12,h20v12',
        spain='h17v04,h17v05',
    )

    def load_in_tiles(arg):
        '''
        Load in tiles by comma separated tiles or shortcut, validate
        that data exists within range.
        '''
        arg = arg.lower()

        if arg in shortcuts:
            print('Used the shortcut:', arg)
            arg = shortcuts[arg]

        generated_list = [coord.strip() for coord in arg.split(',')]

        for item in generated_list:
            regexp = re.fullmatch(r'h(\d\d?)v(\d\d?)', item)
            assert regexp, item
            assert int(regexp.group(1)) in range(36), item
            assert int(regexp.group(2)) in range(18), item

        return generated_list

    def change_output_path(val):
        """Validate that the directory exists """
        assert os.path.isdir(val), repr(val)
        print('Output Path:', val)
        return val

    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '--version',
                        action='version',
                        version=__version__)
    parser.add_argument('--tiles',
                        metavar='tiles or ' + ', '.join(sorted(shortcuts)),
                        help='Location as comma separated tiles or shortcut',
                        default='australia',
                        type=load_in_tiles)
    parser.add_argument('--output-path',
                        metavar='<path>',
                        help='change output path',
                        default=os.environ.get('FMC_PATH', '/g/data/ub8/au/FMC/LVMC/'),
                        type=change_output_path)
    parser.add_argument('--start-year',
                        help='Process start_year to current year, inclusive.',
                        default=2001,
                        type=int)
    return parser.parse_args()


if __name__ == '__main__':
    get_args = cli_get_args()
    print(get_args)
    main(get_args.tiles, get_args.output_path, get_args.start_year)
