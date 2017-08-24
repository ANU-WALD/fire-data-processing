import multiprocessing as mp
from osgeo import gdal
import numpy as np
import sys
from utils import get_top_n_functor, get_fmc_functor, get_tile_map_transformer

def get_fmc_value(rasters, ndvi_raster, auraster, trans, x, y):
    #std_arr = np.zeros((y_size, x_size), dtype=np.float32)
    
    get_top_n = get_top_n_functor()
    get_fmc = get_fmc_functor()
    
    auraster_xsize = auraster.shape[1]
    auraster_ysize = auraster.shape[0]

    map_ij = trans(x, y)

    # This is just to make the example work with a smaller veg mask
    """ 
    if map_ij[0] >= auraster_xsize:
        #print("warning x!", map_ij, auraster.shape)
        #sys.exit()
        #map_ij = [auraster.shape[1]-1, map_ij[1]]
        continue
    if map_ij[1] >= auraster_ysize:
        #print("warning y!", map_ij, auraster.shape)
        #sys.exit()
        #map_ij = [map_ij[0], auraster.shape[0]-1]
        continue
    """
    
    vegtype_value = auraster[map_ij[1], map_ij[0]]

    print("DEBUG: VEGTYPE VALUE:", vegtype_value)

    print("DEBUG: BAND VALUES:", rasters[y, x, :])

    print("DEBUG: X Y", x, y)
    print("DEBUG: NDVI VALUE", ndvi_raster[y, x])

    if vegtype_value > .0 and ndvi_raster[y, x] > .15:
        top_40 = get_top_n(rasters[y, x, :], vegtype_value, 40)
        value = get_fmc(top_40)
        return value#, std_arr

    else:
        return None

def pixel_extractor(tile_path, map_path, x, y):
    
    output = mp.Queue()
    
    trans = get_tile_map_transformer(tile_path, map_path)

    #bands = [gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band{}'.format(tile_path, b)) for b in [1, 2, 3, 4, 5, 6, 7]]
    #Special case where we don't use all the bands 1, 2, 4, 6, 7
    bands = [gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band{}'.format(tile_path, b)) for b in [1, 2, 4, 6, 7]]

    #rasters = [band.GetRasterBand(1).ReadAsArray() for band in bands]
    
    raster_stack = bands[0].GetRasterBand(1).ReadAsArray() * .0001
    for b in range(1, len(bands)):
        raster_stack = np.dstack((raster_stack, bands[b].GetRasterBand(1).ReadAsArray() * .0001))
        
    #raster_stack = np.dstack((raster_stack, (raster_stack[:, :, 5]-raster_stack[:, :, 1])/(raster_stack[:, :, 5]+raster_stack[:, :, 1])))
    # VDII compositions between bands 2 and 6 -> indexes 1 and 3
    raster_stack = np.dstack((raster_stack, (raster_stack[:, :, 1]-raster_stack[:, :, 3])/(raster_stack[:, :, 1]+raster_stack[:, :, 3])))
    #raster stack contains 6 bands: 5 bands from the sat rasters and the VDII one

    ndvi_raster = (raster_stack[:, :, 1]-raster_stack[:, :, 0])/(raster_stack[:, :, 1]+raster_stack[:, :, 0])


    auds = gdal.Open(map_path)
    auraster = auds.GetRasterBand(1).ReadAsArray()
    
    mean_value = get_fmc_value(raster_stack, ndvi_raster, auraster, trans, x, y)

    return mean_value

if __name__ == "__main__":

    #/g/data1/fj2/MODIS/MCD43A4.005/2002.09.06/
    tile = "MCD43A4.A2002249.h30v12.005.2007201174136.hdf"

    x, y = 500, 1100

    mean_value = pixel_extractor("/g/data1/fj2/MODIS/MCD43A4.005/2002.09.06/" + tile,
                         "/g/data1/xc0/original/landcover/aus/Land_cover_for_Au_2002-2013/Landcovermap_merged/Landcovermap_AU_merged_2010-2011.tif", x, y)

    print(mean_value)    
    #print("RESULT: MEAN VALUE", str(mean_value))
