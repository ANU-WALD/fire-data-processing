import multiprocessing as mp
from osgeo import gdal
import numpy as np
from utils_np import get_top_n_functor, get_fmc_functor, get_tile_map_transformer

def get_fmc_image(output, rasters, ndvi_raster, auraster, trans, x_offset, y_offset, tile_size=100):
    mean_arr = np.zeros((tile_size, tile_size), dtype=np.float32)
    #std_arr = np.zeros((y_size, x_size), dtype=np.float32)
    
    get_top_n = get_top_n_functor()
    get_fmc = get_fmc_functor()


    """ Remove after processing Tasmanian tiles 
    auraster_xsize = auraster.shape[1]
    auraster_ysize = auraster.shape[0]
    """
    
    for i in range(tile_size):
        for j in range(tile_size):
            map_ij = trans(x_offset + i, y_offset + j)


            """ Remove after processing Tasmanian tiles """
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

            #if vegtype_value > .0:
            if vegtype_value > .0 and ndvi_raster[j, i] > .15:
                top_40 = get_top_n(rasters[j, i, :], vegtype_value, 40)
                mean_arr[j, i] = get_fmc(top_40)

    output.put((mean_arr, x_offset, y_offset))#, std_arr

def aggregator(tile_path, map_path, tile_size):
    
    output = mp.Queue()
    
    trans = get_tile_map_transformer(tile_path, map_path)
    
    #bands = [gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band{}'.format(tile_path, b)) for b in [1, 2, 3, 4, 5, 6, 7]]
    
    #Special case where we don't use all the bands 1, 2, 4, 6, 7
    bands = [gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band{}'.format(tile_path, b)) for b in [1, 2, 4, 6, 7]]

    #rasters = [band.GetRasterBand(1).ReadAsArray() for band in bands]
    
    raster_stack = bands[0].GetRasterBand(1).ReadAsArray() * .0001
    for b in range(1, len(bands)):
        raster_stack = np.dstack((raster_stack, bands[b].GetRasterBand(1).ReadAsArray() * .0001))
        
    # VDII compositions between bands 2 and 6 -> indexes 1 and 3
    raster_stack = np.dstack((raster_stack, (raster_stack[:, :, 1]-raster_stack[:, :, 3])/(raster_stack[:, :, 1]+raster_stack[:, :, 3])))
    #raster stack contains 6 bands: 5 bands from the sat rasters and the VDII one

    ndvi_raster = (raster_stack[:, :, 1]-raster_stack[:, :, 0])/(raster_stack[:, :, 1]+raster_stack[:, :, 0])


    auds = gdal.Open(map_path)
    auraster = auds.GetRasterBand(1).ReadAsArray()
    
    x_size, y_size = bands[0].RasterXSize, bands[0].RasterYSize
    mean_arr = np.zeros((y_size, x_size), dtype=np.float32)
    
    processes = []
    for x in range(0, 2400, tile_size):
        for y in range(0, 2400, tile_size): 
            processes.append(mp.Process(target=get_fmc_image, args=(output, raster_stack[y:y+tile_size, x:x+tile_size, :], 
                                                                    ndvi_raster[y:y+tile_size, x:x+tile_size],
                                                                    auraster, trans, x, y, tile_size)))
    
    # Run processes
    for p in processes:
        p.start()

    for _ in processes:
        tessera, x_offset, y_offset = output.get()
        mean_arr[y_offset:y_offset+tile_size, x_offset:x_offset+tile_size] = tessera

    # Exit the completed processes
    for p in processes:
        p.join()

    return mean_arr

if __name__ == "__main__":

    """
    tiles = ["MCD43A4.A2010049.h32v10.005.2010068172513.hdf",
             "MCD43A4.A2010049.h32v11.005.2010068075524.hdf",
             "MCD43A4.A2010049.h31v10.005.2010068183638.hdf",
             "MCD43A4.A2010049.h31v11.005.2010068145740.hdf",
             "MCD43A4.A2010049.h31v12.005.2010068070949.hdf",
             "MCD43A4.A2010049.h30v10.005.2010068123759.hdf",
             "MCD43A4.A2010049.h30v11.005.2010068185946.hdf",
             "MCD43A4.A2010049.h30v12.005.2010068101550.hdf",
             "MCD43A4.A2010049.h29v10.005.2010068201929.hdf",
             "MCD43A4.A2010049.h29v11.005.2010068212928.hdf",
             "MCD43A4.A2010049.h29v12.005.2010068191059.hdf",
             "MCD43A4.A2010049.h28v10.005.2010068071924.hdf",
             "MCD43A4.A2010049.h28v11.005.2010068172802.hdf",
             "MCD43A4.A2010049.h28v12.005.2010068210101.hdf",
             "MCD43A4.A2010049.h27v11.005.2010068045632.hdf",
             "MCD43A4.A2010049.h27v12.005.2010068125419.hdf",
             "MCD43A4.A2010049.h28v13.005.2010068121247.hdf",
             "MCD43A4.A2010049.h29v13.005.2010068140914.hdf",
             "MCD43A4.A2010049.h30v13.005.2010068233224.hdf"]
    """

    tiles = ["MCD43A4.A2002249.h30v12.005.2007201174136.hdf"]

    for tile in tiles:

        arr = aggregator("/g/data1/fj2/MODIS/MCD43A4.005/2002.09.06/" + tile,
                         "/g/data1/xc0/original/landcover/aus/Land_cover_for_Au_2002-2013/Landcovermap_merged/Landcovermap_AU_merged_2002-2003.tif", 400)
    
        np.save("./" + tile[:-4], arr)
