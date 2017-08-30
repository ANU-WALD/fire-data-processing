
import datetime
import json
from os import path

from osgeo import gdal
import numpy as np
import netCDF4


def get_nc_name(hdf_tile_path, dest):
    fname = path.basename(hdf_tile_path).replace('.hdf', '_LFMC.nc')
    return path.join(dest, fname)


def pack_data(hdf_file, mean_arr, std_arr, dest):

    file_name = get_nc_name(hdf_file, dest)

    with open('nc_metadata.json') as data_file:
        attrs = json.load(data_file)

    ds = gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band1'.format(hdf_file))
    proj_wkt = ds.GetProjection()
    geot = ds.GetGeoTransform()
    x_size, y_size = ds.RasterXSize, ds.RasterYSize

    with netCDF4.Dataset(file_name, 'w', format='NETCDF4_CLASSIC') as dest:
        for key in attrs:
            setattr(dest, key, attrs[key])
        setattr(dest, "date_created",
                datetime.datetime.now().isoformat(timespec='minutes'))

        var = dest.createVariable("x", "f8", ("x",))
        var.units = "m"
        var.long_name = "x coordinate of projection"
        var.standard_name = "projection_x_coordinate"
        var[:] = np.linspace(geot[0], geot[0]+(geot[1]*x_size), x_size)

        var = dest.createVariable("y", "f8", ("y",))
        var.units = "m"
        var.long_name = "y coordinate of projection"
        var.standard_name = "projection_y_coordinate"
        var[:] = np.linspace(geot[3], geot[3]+(geot[5]*y_size), y_size)

        var = dest.createVariable("lfmc_mean", 'f4', ("y", "x"),
                                  fill_value=np.nan)
        var.long_name = "LFMC Arithmetic Mean"
        var.units = '%'
        var.grid_mapping = "sinusoidal"
        var[:] = mean_arr

        var = dest.createVariable("lfmc_stdv", 'f4', ("y", "x"),
                                  fill_value=np.nan)
        var.long_name = "LFMC Standard Deviation"
        var.units = '%'
        var.grid_mapping = "sinusoidal"
        var[:] = std_arr

        var = dest.createVariable("sinusoidal", 'S1', ())

        var.grid_mapping_name = "sinusoidal"
        var.false_easting = 0.0
        var.false_northing = 0.0
        var.longitude_of_central_meridian = 0.0
        var.longitude_of_prime_meridian = 0.0
        var.semi_major_axis = 6371007.181
        var.inverse_flattening = 0.0
        var.spatial_ref = proj_wkt
        var.GeoTransform = ' '.join(str(geot[i]) for i in range(6))


def get_top_n_functor(n=40):
    # Notes: FMC.npy should be a column in the lookup table; after we
    # get the ton N indicies (below) we use them to select FMC here.
    fmc = np.load("./FMC.npy")
    lut = np.load("./LUT.npy")[:, [0,1,3,5,6,7]]
    lut_sq = np.sqrt(np.einsum('ij,ij->i', lut, lut))

    def get_top_n(mb, veg_type, top_n=n, mat=lut, smat=lut_sq):
        # Select Veg type subset from LUT table
        start, end = {1: (0, 2563), 2: (2563, 4226), 3: (4226, 8708)}[veg_type]
        vmat = mat[start:end]
        vsmat = smat[start:end]
        # Fast calculation of spectral angle between observation and each row
        spectral_angle = np.arccos(
            np.einsum('ij,j->i', vmat, mb) /
            (np.sqrt(np.einsum('i,i->', mb, mb)) * vsmat)
        )
        # Returns indices into the full lookup table for best matches
        idxs = np.argpartition(spectral_angle, top_n)[:top_n] + start
        return fmc[idxs].mean(axis=-1), fmc[idxs].std(axis=-1)

    return get_top_n
