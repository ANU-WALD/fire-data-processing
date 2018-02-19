#!/usr/bin/env python
"""
Distribute a group of MODIS sinusoidal tiles to produce LFMC using Raijin jobs.

Use a comma-separated list for tiles: e.g, h28v13,h29v11 ...
Tile shortcuts include: [Australia, South Africa, Spain]
"""

import os
import re
import sys
import time
import typing as t
import datetime
import argparse
import subprocess

import numpy as np
import xarray as xr

import modis

__version__ = '0.1.0'
run_time = int(time.time())

THIS_YEAR = datetime.date.today().year
OBS_PER_YEAR = 90

shortcuts = dict(
    australia=(
        'h28v13,h29v11,h28v12,h29v10,h29v12,h32v10,h27v11,h31v11,h32v11,'
        'h30v11,h30v10,h27v12,h30v12,h31v12,h31v10,h29v13,h28v11'),
    south_africa='h19v11,h20v11,h21v11,h19v12,h20v12',
    spain='h17v04,h17v05',
)


def qsub(*args: str) -> t.Any:
    """Sumbit a PBS jub and return the numeric ID as a string."""
    return subprocess.run(
        args, check=True, stdout=subprocess.PIPE, encoding='utf-8'
    ).stdout.strip().split('.')[0]


def main(tiles_list: t.List[str], path: str, start_year: int) -> None:
    """Queue all the jobs we need to get a complete updated archive.

    1. Queue all tiles that don't exist + updates for this year
    2. Queue means for all tiles, depending on 2001-2015 tile jobs
    3. Queue a mosiac job for each year; depending tiles for this year,
       means, and the mosiac for last year.

    """
    jobs = dict()
    log_dir = '/g/data/xc0/project/FMC_Australia/logs/'

    # part 1: launch tiles
    for tile in tiles_list:
        masks = modis.get_masks(2013, tile)  # indicative year
        elements = np.sum(masks['forest'] | masks['shrub'] | masks['grass'])
        walltime = int(np.ceil(40 * elements / 2400. ** 2)) + 2

        if start_year != THIS_YEAR:
            print(f'Calculated walltime for tile: {tile} = {walltime}')
        for year in range(start_year, THIS_YEAR + 1):
            fname = os.path.join(path, 'LVMC', f'LVMC_{year}_{tile}.nc')
            if os.path.isfile(fname):
                if year == THIS_YEAR:
                    reflectance = modis.get_reflectance(year, tile)
                    output_dataset = xr.open_dataset(fname)
                    reflectance_times = \
                        reflectance.time[:len(output_dataset.time)]
                    new_obs = len(reflectance.time) - len(output_dataset.time)
                    assert np.all(reflectance_times == output_dataset.time)
                    if not new_obs:
                        print(f'Already done: {fname}')
                        continue
                    walltime = int(np.ceil(
                        40 * elements * (new_obs / OBS_PER_YEAR)
                        / 2400. ** 2 + 0.5)) + 2
                    print(f'Update walltime: {walltime}h for {new_obs} steps')
                else:
                    continue
            print('Submitting job for', fname)
            logfile = f'{log_dir}{run_time}-{year}{tile}-FMC'

            jobs[(year, tile)] = qsub(
                'qsub',
                '-v', f'FMC_YEAR={year},FMC_TILE={tile},FMC_PATH={path+"/LVMC"}',
                '-l', f'walltime={walltime}:00:00',
                '-N', f'{year}{tile}-FMC',
                '-o', f'{logfile}.out',
                '-e', f'{logfile}.err',
                'onetile.qsub'
            )
            job_id = jobs[(year, tile)]
            print(f'Submitted job {job_id} for {year}{tile}')

    if tiles_list != load_in_tiles(shortcuts['australia']):
        print('Can only create mosaics for Australia')
        sys.exit(1)
    # TODO: support this!  Requires upgrades to input location handling
    #       in all scripts and output location in means.py
    if path != '/g/data/ub8/au/FMC/':
        print('ERROR: launchmany does not currently support non-default paths'
              ' for mosaics etc.')
        sys.exit(1)

    # part 2: launch means
    means_depend = ':'.join(j for (yr, _), j in jobs.items() if yr <= 2015)
    if means_depend:
        logfile = f'{log_dir}{run_time}-means-FMC'
        jobs[(0, 'means')] = qsub(
            'qsub',
            '-N', f'means-FMC',
            '-o', f'{logfile}.out',
            '-e', f'{logfile}.err',
            '-W', f'depend=afterok:{means_depend}',
            'means.qsub'
        )
        print(f'Submitted job for means')

    # part 3: launch mosaics
    for year in range(start_year, THIS_YEAR + 1):
        depends_on = [job for (yr, _), job in jobs.items() if yr == year]
        fname = os.path.join(path, f'australia_LVMC_{year}.nc')
        if os.path.isfile(fname) and (year != THIS_YEAR or not depends_on):
            continue
        for key in [(0, 'means'), (year - 1, 'mosaic')]:
            if key in jobs:
                depends_on.append(jobs[key])
        logfile = f'{log_dir}{run_time}-mosiac{year}-FMC'
        depends = ':'.join(depends_on)
        jobs[(year, 'mosaic')] = qsub(
            'qsub',
            '-N', f'{year}mosiac-FMC',
            '-o', f'{logfile}.out',
            '-e', f'{logfile}.err',
            '-W', f'depend=afterok:{depends}',
            'mosaic.qsub'
        )
        print(f'Submitted job for {year} mosaic')


def load_in_tiles(arg: str) -> t.List[str]:
    """
    Load in tiles by comma separated tiles or shortcut.

    Also validate that data exists within range.
    """
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


def cli_get_args() -> argparse.Namespace:
    """Get command line arguments."""
    def change_output_path(val: str) -> str:
        """Validate that the directory exists."""
        assert os.path.isdir(val), repr(val)
        print('Output Path:', val)
        return val

    def check_year(val: str) -> int:
        """Validate the given year."""
        year = int(val)
        assert 2001 <= year <= THIS_YEAR
        return year

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        '-V', '--version',
        action='version',
        version=__version__)
    parser.add_argument(
        '--tiles',
        metavar='<tile>',
        help='location as comma separated tiles or shortcut',
        default='australia',
        type=load_in_tiles)
    parser.add_argument(
        '--output-path',
        metavar='<path>',
        help='change output path',
        default='/g/data/ub8/au/FMC/',
        type=change_output_path)
    parser.add_argument(
        '--start-year',
        metavar='<year>',
        help='process start_year to current year, inclusive.',
        default=2001,
        type=check_year)
    return parser.parse_args()


if __name__ == '__main__':
    get_args = cli_get_args()
    print(get_args)
    main(get_args.tiles, get_args.output_path, get_args.start_year)
