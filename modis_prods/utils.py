from osgeo import gdal
import numpy as np
import netCDF4
#import pyproj
import json
import datetime

"""
def get_coordinate_mesh(geot, x_size, y_size):

    sin_proj4 = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"
    wgs_proj4 = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

    sin_proj = pyproj.Proj(sin_proj4)
    wgs_proj = pyproj.Proj(wgs_proj4)
    
    x_dim = np.arange(geot[0], geot[0]+(x_size)*geot[1], geot[1])
    y_dim = np.arange(geot[3], geot[3]+(y_size)*geot[5], geot[5])

    xs = np.repeat(np.expand_dims(x_dim, axis=0), y_dim.shape[0], axis=0)
    ys = np.repeat(np.expand_dims(y_dim, axis=0), x_dim.shape[0], axis=0).T
    
    sin_proj = pyproj.Proj(sin_proj4)
    wgs_proj = pyproj.Proj(wgs_proj4)
    
    longitudes, latitudes = pyproj.transform(sin_proj, wgs_proj, xs.flatten(), ys.flatten())
    
    return longitudes.reshape((y_size, x_size)), latitudes.reshape((y_size, x_size))

def pack_data_mesh(hdf_file, mean_arr, std_arr, dest):
    
    file_name = get_nc_name(hdf_file, dest)
    
    with netCDF4.Dataset(file_name, 'w', format='NETCDF4') as dest:
        
        setattr(dest, "Conventions", "CF-1.6")
        setattr(dest, "Description", "LFMC Modis MCD43A4 Tiles processing. This product was made possible through funding from the Bushfire and Natural Hazards CRC through the project 'Mapping bushfire hazard and impacts'. Contact: marta.yebra@anu.edu.au Reference; Yebra, M., van Dijk, A., Quan, X.,  Cary, G. Monitoring and forecasting fuel moisture content for Australia using a combination of remote sensing and modelling. Proceedings for the 5th International Fire Behaviour and Fuels Conference. April 11-15, 2016, Melbourne, Australia. Published by the International Association of Wildland Fire, Missoula, Montana, USA. (The code used to generate this product was implemented by Pablo Rozas Larraondo at the National Computational Infrastructure)") 
        ds = gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band1'.format(hdf_file))
        geot = ds.GetGeoTransform()

        lons, lats = get_coordinate_mesh(geot, ds.RasterXSize, ds.RasterYSize)

        x_dim = dest.createDimension("XDim", ds.RasterXSize)
        y_dim = dest.createDimension("YDim", ds.RasterYSize)

        var = dest.createVariable("latitude", "f8", ("YDim", "XDim"))
        var.coordinates = "latitude longitude"
        var.eoslib = "Calculated latitude"
        var.units = 'degrees_north'
        var.long_name = "/MOD_Grid_BRDF/latitude"
        var.standard_name = "Latitude"
        var[:] = lats

        var = dest.createVariable("longitude", "f8", ("YDim", "XDim"))
        var.coordinates = "latitude longitude"
        var.eoslib = "Calculated longitude"
        var.units = 'degrees_east'
        var.long_name = "/MOD_Grid_BRDF/longitude"
        var.standard_name = "Longitude"
        var[:] = lons
        
        var = dest.createVariable("lfmc_mean", "f4", ("YDim", "XDim"), fill_value=.0)
        var.coordinates = "latitude longitude"
        var.long_name = "LFMC Arithmetic Mean"
        var.units = '%'
        var[:] = mean_arr
        
        var = dest.createVariable("lfmc_stdv", "f4", ("YDim", "XDim"), fill_value=.0)
        var.coordinates = "latitude longitude"
        var.long_name = "LFMC Standard Deviation"
        var.units = '%'
        var[:] = std_arr
        
        var = dest.createVariable("crs", "f4", ())
        var.projection_name = "GCTP_SNSOID"
        var.geotransform = geot
        var.proj4 = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"
"""

def get_nc_name(hdf_tile_path, dest):
    
    return dest + hdf_tile_path.split("/")[-1][:-4] + "_LFMC.nc"


def pack_data(hdf_file, mean_arr, std_arr, dest):
    
    file_name = get_nc_name(hdf_file, dest)
    
    with netCDF4.Dataset(file_name, 'w', format='NETCDF4_CLASSIC') as dest:
        with open('nc_metadata.json') as data_file:
            attrs = json.load(data_file)
            for key in attrs:
                setattr(dest, key, attrs[key])
        setattr(dest, "date_created", datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))
        
        ds = gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band1'.format(hdf_file))
        proj_wkt = ds.GetProjection()
        geot = ds.GetGeoTransform()
        
        x_dim = dest.createDimension("x", ds.RasterXSize)
        y_dim = dest.createDimension("y", ds.RasterYSize)

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
    
    return np.array([geot[1], .0, geot[0], .0, geot[5], geot[3], .0, .0, 1.]).reshape((3,3))
    

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
        mean = np.einsum('i->', fmc[idxs])/idxs.shape[0]
        return mean, np.sqrt(np.einsum('i->',(fmc[idxs]-mean)**2)/idxs.shape[0])

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

        err = np.arccos(np.einsum('ij,j->i', vmat, mb)/(np.einsum('i,i->', mb, mb)**.5*vsmat))

        idxs = np.argpartition(err, top_n)[:top_n] + idx[0]

        return idxs

    return get_top_n

if __name__ == "__main__":

    pass

