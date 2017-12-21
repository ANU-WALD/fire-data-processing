# Super duper crude script to get quick results.  Sorry.

# qsub -N SPOT-namadgi spot.qsub
# or
# qsub -v "FMC_SPOT_LOCATION=canberra" -l walltime=20:00:00 -N SPOT-canberra spot.qsub

import os
from concurrent.futures import ProcessPoolExecutor

import xarray as xr

import onetile


def main():
    """Processes a SPOT cube.  Set env var FMC_SPOT_BIGGER for second file."""
    location = os.environ.get('FMC_SPOT_LOCATION', 'namadgi')
    assert location in ('canberra', 'namadgi')
    fname = '/g/data/xc0/project/sensors2solutions/SPOT_{}.nc'.format(location)

    ds = xr.open_dataset(fname)
    ds['time'] = ds.time.astype('M8')

    def one_step(ts):
        satellite = str(ds.sel(time=ts).sensor.values)
        return onetile.get_fmc(ds.sel(time=ts).load(), satellite=satellite)

    workers = 6 if location == 'namadgi' else 8
    with ProcessPoolExecutor(workers) as pool:
        steps = pool.map(one_step, ds.time)
    fmc = xr.concat(steps, dim=ds.time)
    fmc.to_netcdf(fname.rstrip('.nc') + '_lvmc.nc')


if __name__ == '__main__':
    main()
