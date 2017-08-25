from osgeo import gdal
import numpy as np
import netCDF4
#import pyproj
import json
import datetime


def get_nc_name(hdf_tile_path, dest):
    return dest + hdf_tile_path.split("/")[-1][:-4] + "_LFMC.nc"


def pack_data(hdf_file, mean_arr, std_arr, dest):

    file_name = get_nc_name(hdf_file, dest)

    with netCDF4.Dataset(file_name, 'w', format='NETCDF4_CLASSIC') as dest:
        with open('nc_metadata.json') as data_file:
            attrs = json.load(data_file)
        for key in attrs:
            setattr(dest, key, attrs[key])
        setattr(dest, "date_created",
                datetime.datetime.now().isoformat(timespec='minutes'))

        ds = gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band1'.format(hdf_file))
        proj_wkt = ds.GetProjection()
        geot = ds.GetGeoTransform()

        var = dest.createVariable("x", "f8", ("x",))
        var.units = "m"
        var.long_name = "x coordinate of projection"
        var.standard_name = "projection_x_coordinate"
        var[:] = np.linspace(geot[0], geot[0]+(geot[1]*ds.RasterXSize), ds.RasterXSize)

        var = dest.createVariable("y", "f8", ("y",))
        var.units = "m"
        var.long_name = "y coordinate of projection"
        var.standard_name = "projection_y_coordinate"
        var[:] = np.linspace(geot[3], geot[3]+(geot[5]*ds.RasterYSize), ds.RasterYSize)

        var = dest.createVariable("lfmc_mean", 'f4', ("y", "x"), fill_value=.0)
        var.long_name = "LFMC Arithmetic Mean"
        var.units = '%'
        var.grid_mapping = "sinusoidal"
        var[:] = mean_arr

        var = dest.createVariable("lfmc_stdv", 'f4', ("y", "x"), fill_value=.0)
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
        var.GeoTransform = "{} {} {} {} {} {} ".format(*[geot[i] for i in range(6)])


# All Modis 7 bands are 2400x2400 so we just get geotransform for Band1
def get_affine(geot):
    out = [geot[1], 0., geot[0], 0., geot[5], geot[3], 0., 0., 1.]
    return np.array(out).reshape((3, 3))


def transform(geot, i, j):
    return tuple(np.dot(get_affine(geot), np.array([i, j, 1]))[:2])


def transform_inv(geot, x, y):
    return tuple(np.dot(np.linalg.inv(get_affine(geot)), np.array([x, y, 1]))[:2])


def get_tile_map_transformer(tile_path, map_path):

    tile = gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band1'.format(tile_path))
    tile_geot = tile.GetGeoTransform()

    aumap = gdal.Open(map_path)
    map_geot = aumap.GetGeoTransform()

    def transformer(x, y):
        idx = transform_inv(map_geot, *transform(tile_geot, x, y))
        return (int(round(idx[0])), int(round(idx[1])))

    return transformer


def get_fmc_functor():
    # Load FMC table
    fmc = np.load("./FMC.npy")

    def get_fmc(idxs, fmc=fmc):
        # Select Veg type subset from LUT table
        mean = np.einsum('i->', fmc[idxs]) / idxs.shape[0]
        athing = np.einsum('i->', (fmc[idxs] - mean) ** 2) / idxs.shape[0]
        return mean, np.sqrt(athing)

    return get_fmc


def get_vegtype_idx(veg_type):
    if veg_type == 1.:
        return (0, 2563)
    elif veg_type == 2.:
        return (2563, 4226)
    elif veg_type == 3.:
        return (4226, 8708)


def get_top_n_functor():
    # Read the LUT table
    lut = np.load("./LUT.npy")
    lut = lut[:, [0,1,3,5,6,7]]

    lut_sq = np.sqrt(np.einsum('ij,ij->i',lut, lut))

    def get_top_n(mb, veg_type, top_n, mat=lut, smat=lut_sq):

        idx = get_vegtype_idx(veg_type)

        # Select Veg type subset from LUT table
        vmat = mat[idx[0]:idx[1], :]
        vsmat = smat[idx[0]:idx[1]]

        err = np.arccos(
            np.einsum('ij,j->i', vmat, mb) /
            (np.einsum('i,i->', mb, mb) ** .5 * vsmat)
        )

        idxs = np.argpartition(err, top_n)[:top_n] + idx[0]

        return idxs

    return get_top_n
