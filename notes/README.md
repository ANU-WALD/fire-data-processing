# Reference material

This directory contains various bits of information about

- parts of the existing system
- location of useful datasets
- plans for implementing a clean and integrated version

------------------------

Previously generated data is mostly under /g/data1/xc0/project/FMC_Australia/
Some is under /g/data1/ub8/au/ (so it's visible to Thredds)


https://github.com/monkeybutter/netcdf_packer/blob/master/modis_packer.py
This is the script that aggregated our current FMC data, which has the
sinusoidal projection variable and metadata that GSKY requires
(whatever that is).
Note that it does not actually calculate the FMC values from MODIS data.


All previous data has been derived from MODIS collection five, which
was discontinued in early 2017.  The new version will therefore be based
on collection six.

Landsat Collection Six data can be found at
/g/data/u39/public/data/modis/lpdaac-tiles-c6/

This is in HDF format.  Xarray supports PyNIO as a backend to read this,
but as of 2017-08-18 PyNIO does not support Python3 (though there's a port
in progress - https://github.com/NCAR/pynio/issues/10 ).

I think our best option is to target Python 3.6, but accept that it will
have to run under 2.7 at least to start with.
