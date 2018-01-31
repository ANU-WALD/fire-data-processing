"""
Process LFMC data for a specific SPOT cube using onetile functions.

The SPOT cube uses top of atmosphere radiance as opposed to corrected surface
reflectance (which is used by MODIS).

Spot.py is not covered by launchmany.py, therefore NCI Raijin job schedule
commands are included below:

qsub -N SPOT-namadgi spot.qsub

or

qsub -v "FMC_SPOT_LOCATION=canberra" -l walltime=20:00:00 -N SPOT-canberra
spot.qsub
"""

import os
import datetime

import xarray as xr

import onetile


def report(*args: str) -> None:
    """Print script status reports."""
    print('at {}:  {}'.format(datetime.datetime.now(), ' '.join(args)))


def main() -> None:
    """Process a SPOT cube.  Set env var FMC_SPOT_BIGGER for second file."""
    location = os.environ.get('FMC_SPOT_LOCATION', 'namadgi')
    assert location in ('canberra', 'namadgi')
    fname = '/g/data/xc0/project/sensors2solutions/SPOT_{}.nc'.format(location)

    ds = xr.open_dataset(fname).load()
    ds['time'] = ds.time.astype('M8')
    report('data loaded')

    steps = []
    for ts in ds.time:
        date = str(ts.to_pandas())[:10]
        step_fname = fname.rstrip('.nc') + '_{}_lvmc.nc'.format(date)
        try:
            steps.append(xr.open_dataset(step_fname))
            report('already written', step_fname)
            continue
        except Exception:
            pass
        report('processing', date)
        satellite = str(ds.sel(time=ts).sensor.values)
        data = onetile.get_fmc(ds.sel(time=ts).load(), satellite=satellite)
        steps.append(data)
        data.to_netcdf(step_fname)
        report('done', date)
    fmc = xr.concat(steps, dim=ds.time)
    fmc.to_netcdf(fname.rstrip('.nc') + '_lvmc.nc')


if __name__ == '__main__':
    report('starting')
    main()
