from numpy import *
from osgeo import gdal
from affine import Affine
import pandas as pd
import numpy as np
from numba import jit

# All Modis 7 bands are 2400x2400 so we just get geotransform for Band1
def get_tile_map_transformer(tile_path, map_path):

    tile = gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band1'.format(tile_path))
    tile_geot = tile.GetGeoTransform()
    
    aumap = gdal.Open(map_path)
    map_geot = aumap.GetGeoTransform()
    
    tile_fwd = Affine.from_gdal(*tile_geot)
    au_fwd = Affine.from_gdal(*map_geot)
    
    def transformer(x, y):
        idx = ~au_fwd * (tile_fwd * (x, y))
        return (int(round(idx[0])), int(round(idx[1])))
    
    return transformer


def get_fmc_functor():
    # Load FMC table
    df = pd.read_csv("./FMC.txt", sep='\t', header=None, index_col=0)

    def get_fmc(idxs, df=df):
        # Select Veg type subset from LUT table
        fmc = df.loc[idxs]

        #print("DEBUG: FMC VALUES:", fmc, fmc[1])

        return np.mean(fmc[1])#, np.std(fmc[1])

    return get_fmc

@jit
def get_vegtype_idx(veg_type):
    if veg_type == 1.:
        return (1, 2563)
    elif veg_type == 2.:
        return (2564, 4226)
    elif veg_type == 3.:
        return (4227, 8708)


def get_top_n_functor():
    # Read the LUT table
    df = pd.read_csv("./LUT.txt", sep='\t', header=None, index_col=0)
    df = df[[1,2,4,6,7,8]]

    def squarer(x):    
        return (x[1]**2 + x[2]**2 + x[4]**2 + x[6]**2 + x[7]**2 + x[8]**2)**.5
     
    lut_sq = df.apply(squarer, axis=1).values

    lut_mat = np.array(df.values)

    def get_top_n(mb, veg_type, top_n, mat=lut_mat, smat=lut_sq):

        # Get indexes for veg_type class
        #start = time.time()
        idx = get_vegtype_idx(veg_type)
        #end = time.time()
        #print(end - start)

        # Select Veg type subset from LUT table
        #start = time.time()
        #vt = df.loc[idx[0]:idx[1]].copy(deep=True)
        vmat = mat[idx[0]-1:idx[1], :]

        vsmat = smat[idx[0]-1:idx[1]]

        print("DEBUG mat", mat[:2, :])
        print("DEBUG vmat", vmat[:2, :])
        print("DEBUG smat", smat[:2])

        err = get_sa2(vmat, vsmat, mb)

        print("DEBUG err", err[:2])

        #start = time.time()
        idxs = err.argsort()[:top_n] + idx[0]
        print("DEBUG", idxs)

        #print("DEBUG: TOP 40 INDEXES:", idxs)
        #end = time.time()
        #print(end - start)

        return idxs

    return get_top_n

@jit(nopython=True)
def get_rmse(table, image):
    err = np.zeros(table.shape[0])
    for i in range(err.shape[0]):
        err[i] = np.sum(((table[i] - image)**2))**.5

    return err


@jit(nopython=True)
def get_sa(table, sq_table, image):
    sq_data = (image[0]**2 + image[1]**2 + image[2]**2 + image[3]**2 + image[4]**2 + image[5]**2)**.5

    #print("DEBUG: pixel data:", image)
    #print("DEBUG: pixel squared data:", sq_data)
    #print("DEBUG: first value of LUT table:", table[0])
    #print("DEBUG: first value of SQ_LUT table:", sq_table[0])
    sq_sum = image[0]*table[0][0] + image[1]*table[0][1] + image[2]*table[0][2] + \
             image[3]*table[0][3] + image[4]*table[0][4] + image[5]*table[0][5]
    #print("DEBUG: first value of SQ SUM:", sq_sum)
    sa = np.arccos(sq_sum/(sq_data*sq_table[0]))
    #print("DEBUG: first value of SA:", sa)


    sa = np.zeros(table.shape[0])
    for i in range(sa.shape[0]):
        sq_sum = image[0]*table[i][0] + image[1]*table[i][1] + image[2]*table[i][2] + \
                 image[3]*table[i][3] + image[4]*table[i][4] + image[5]*table[i][5]

        sa[i] = np.arccos(sq_sum/(sq_data*sq_table[i]))

    return sa

#@jit(cache=True)
def get_sa2(table, sq_table, image):
    sq_data = np.sum(np.multiply(image, image))**.5
    #sa = np.zeros(table.shape[0])
    sq_sum = np.sum(np.multiply(table, image), axis=1)

    #sa = np.arccos(sq_sum/(sq_data*sq_table))

    return np.arccos(sq_sum/(sq_data*sq_table))

"""
def get_raster_values(rasters, i, j):
    raster_values = np.zeros((len(rasters)+1))

    for idx, b in enumerate(range(len(rasters))):
        raster_values[idx] = rasters[b][j, i]*.0001

    raster_values[-1] = (raster_values[5]-raster_values[1])/(raster_values[5]+raster_values[1])

    return raster_values
"""


