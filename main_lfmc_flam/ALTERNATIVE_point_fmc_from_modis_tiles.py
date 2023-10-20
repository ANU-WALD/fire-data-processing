import pandas as pd
from osgeo import gdal
from glob import glob
import numpy as np
from datetime import datetime, timedelta
import xarray as xr
import argparse
from pyproj import Proj, transform



# match land cover IDs with land cvoer description
LC_model = {0: 'Others',
            1: 'Grass',
            2: 'Shrub',
            3: 'Forest'}
LC_modis = {1:'Evergreen Needleleaf Forests',
            2:'Evergreen Broadleaf Forests',
            3:'Deciduous Needleleaf Forests',
            4:'Deciduous Broadleaf Forests',
            5:'Mixed Forests',
            6:'Closed Shrublands',
            7:'Open Shrublands',
            8:'Woody Savannas',
            9:'Savannas',
            10:'Grasslands',
            11:'Permanent Wetlands',
            12:'Croplands',
            13:'Urban and Built-up Lands',
            14:'Cropland/Natural Vegetation Mosaics',
            15:'Permanent Snow and Ice',
            16:'Barren',
            17:'Water Bodies'
            }



def tile_idx_x_y(tile_name, x, y, geot_tile):
    res = geot_tile[1]

    x_min = tiles_borders[tile_name][0] + res/2 # x of centre of leftmost pixels
    x_max = tiles_borders[tile_name][1] - res/2 # x of centre of rightmost pixels
    y_min = tiles_borders[tile_name][3] + res/2 # y of centre of bottom pixels
    y_max = tiles_borders[tile_name][2] - res/2 # y of centre of top pixels

    x_dim = np.linspace(x_min, x_max, 2400)  # coords of centre of pixels, 2400 is size of tiles
    y_dim = np.linspace(y_max, y_min, 2400)

    idx_x = abs(x_dim-x).argmin()
    idx_y = abs(y_dim-y).argmin()

    return idx_x, idx_y 




# function to get vegetation type mask
def get_vegmask(tile_id, tile_date, idx_x, idx_y):
    mask_paths = sorted(glob('{}/*'.format(mcd12q1_path)))[::-1]

    # Find the most recent mask for the FMC data
    for mask_path in mask_paths:
        msk_date =  datetime.strptime(mask_path.split('/')[-1], '%Y.%m.%d')
        if msk_date > tile_date:
            continue
        
        files = glob('{0}/MCD12Q1.A{1}{2:03d}.{3}.061.*.hdf'.format(mask_path, msk_date.year, msk_date.timetuple().tm_yday, tile_id))
        
        if len(files) == 1:
            veg_mask = xr.open_dataset(files[0]).LC_Type1[:].data[idx_y, idx_x]

            if veg_mask in [1,2,3,4,5,8,9]:
                veg_mask_model = 3
            elif veg_mask in [6,7]:
                veg_mask_model = 2
            elif veg_mask in [10,12]:
                veg_mask_model = 1
            else:
                veg_mask_model = 0

            return veg_mask_model, veg_mask
    
    return None




# function to select grass, shrub, or tree LUT
def get_vegtype_idx(veg_type):
    if veg_type == 1.:
        return (0, 2563)
    elif veg_type == 2.:
        return (2563, 4226)
    elif veg_type == 3.:
        return (4226, 8708)
    



# function to get 40 (in thise case) most similar spectra from the LUT
def get_top_n_functor():
    # Read the LUT table
    lut = np.load('./LUT.npy')
    lut = lut[:, [0,1,3,5,6,7]]
    lut_sq = np.sqrt(np.einsum('ij,ij->i',lut, lut))

    def get_top_n(mb, veg_type, top_n, mat=lut, smat=lut_sq):
        idx = get_vegtype_idx(veg_type)

        # Select Veg type subset from LUT table
        vmat = mat[idx[0]:idx[1], :]
        vsmat = smat[idx[0]:idx[1]]

        # This is a computational trick that results in a +2x speedup of the code
        # arccos is a decreaing function in the [-1,1] range so we can replace this
        # with a constant linear function as we are only interested in the relative values.
        #err = np.arccos(np.einsum('ij,j->i', vmat, mb)/(np.einsum('i,i->', mb, mb)**.5*vsmat))
        err = -1*np.einsum('ij,j->i', vmat, mb)/(np.einsum('i,i->', mb, mb)**.5*vsmat)

        idxs = np.argpartition(err, top_n)[:top_n] + idx[0]

        return idxs

    return get_top_n




# function to compute median of 40 LFMC values from 40 most simalr spectra
def get_fmc_functor_median():
    # Load FMC table
    fmc = np.load('./FMC.npy')
    
    def get_fmc_median(idxs, fmc=fmc):
        # Select Veg type subset from LUT table
        median = np.nanmedian(fmc[idxs])
        return median

    return get_fmc_median




# function to extract reflectance data from MODIS 
def get_reflectances(tile_file, idx_x, idx_y):
    #Special case where we don't use all the bands, only bands 1, 2, 4, 6, 7 are needed for the LUTs
    bands = [1,2,4,6,7]

    # sometimes band 6 (maybe also other bands?) has more missing data than other bands, 
    # the following mask is to make sure the final LFMC images are composed only by pixels present in all bands, to avoid artifacts
    band_mask = list()
    ref_stack = list()
    q_mask = list()

    for i in bands:
        ref_value = tile_file["Nadir_Reflectance_Band{}".format(i)].data[idx_y, idx_x].astype(np.float32)
        ref_stack.append(ref_value)
        q_mask.append(tile_file["BRDF_Albedo_Band_Mandatory_Quality_Band{}".format(i)].data[idx_y, idx_x])
        band_mask.append(~np.isnan(ref_value))
    
    # NDII6 compositions between bands 2 and 6 -> indexes 1 and 3
    ndii6 = (ref_stack[1]-ref_stack[3])/(ref_stack[1]+ref_stack[3])
    ref_stack.append(ndii6)

    q_mask = q_mask == [0]*len(q_mask)
    band_mask = np.all(band_mask)

    return np.array(ref_stack), q_mask, band_mask # need to convert list ref_stack in 1D array to simulate 1D array taken from data cube with coords y and x and reflectance on the 3rd axis



# function to create LFMC array  
def fmc(ref_stack, q_mask, veg_type, band_mask):
    #quality mask is actually not used because pixels with perfect quality for all bands are very few actually
    ndvi_raster = (ref_stack[1]-ref_stack[0])/(ref_stack[1]+ref_stack[0])

    get_top_n = get_top_n_functor()
    get_fmc = get_fmc_functor_median()
    
    if veg_type > 0 and ndvi_raster > .15 and band_mask:
        top_40 = get_top_n(ref_stack, veg_type, 40)  
        median_lfmc = get_fmc(top_40)  
        return median_lfmc
    else:
        return 'NA'



# function to compute LFMC
def get_lfmc(tile_name, tile_file, date_time, x, y, geot_tile):
    idx_x, idx_y = tile_idx_x_y(tile_name, x, y, geot_tile)

    veg_type_model, veg_type_modis = get_vegmask(tile_name, date_time, idx_x, idx_y)  
    ref_stack, q_mask, band_mask = get_reflectances(tile_file, idx_x, idx_y) 
    fmc_value = fmc(ref_stack, q_mask, veg_type_model, band_mask) 

    return fmc_value, veg_type_model, veg_type_modis





# example for running script
# /g/data/xc0/software/conda-envs/rs3/bin/python ALTERNATIVE_point_LFMC_from_MODIS_tiles.py -table /g/data/.../table.csv -out /g/data/.../table_final.csv -xcol X_sinu -ycol Y_sinu -datecol Date -proj sinusoidal -lag 8


if __name__=='__main__':
    parser = argparse.ArgumentParser(description="""FMC from point locations argument parser""")
    parser.add_argument('-table', '--pointcsvtable', type=str, required=True, help="Full path to csv table with points coords")
    parser.add_argument('-out', '--outputpath', type=str, required=True, help="Full path for the output")
    parser.add_argument('-xcol', '--xcolname', type=str, required=True, help="name of column containing x or lon coordinate")
    parser.add_argument('-ycol', '--ycolname', type=str, required=True, help="name of column containing y or lat coordinate")
    parser.add_argument('-datecol', '--datecolname', type=str, required=True, help="name of column containing the dates")
    parser.add_argument('-proj', '--projection', type=str, required=True, help="projection of coords in csv file, either wgs84 or sinusoidal")
    parser.add_argument('-lag', '--lagdays', type=int, required=True, help="lag days prior to dates reported in table, write 0 if want to extract on the exact dates")
    args = parser.parse_args()


    #========= THIS PART MIGHT NEED TO BE ADAPTED ACCORDING TO WHAT NEEDED ====================================
    path_to_modis = '/g/data/ub8/au/FMC/intermediary_files/NSW_MCD43A4.061' # this might need to be downloaded. NSW tiles:  'h29v12', 'h30v12', 'h30v11', 'h31v11', 'h31v12'
    mcd12q1_path = '/g/data/ub8/au/FMC/intermediary_files/MCD12Q1.061'

    tiles = ['h29v12', 'h30v11', 'h30v12', 'h31v11', 'h31v12'] # tiles where points are contained
    #==========================================================================================================
     

    LONGLAT_WGS84 = Proj('+proj=longlat +datum=WGS84 +no_defs')
    MODIS_SINUSOIDAL = Proj("+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs")

    ds = pd.read_csv(args.pointcsvtable)
    df = ds.copy()

    x_col_name, y_col_name = args.xcolname, args.ycolname #name columns coords

    df['tile'] = np.nan
    df['LFMC'] = np.nan
    df['LFMC_date'] = np.nan
    df['LC_model_id'] = np.nan # ID of Land Cover tyep as used in the model to retrive LFMC
    df['LC_model'] = np.nan # name of Land Cover type as used in the model to retrive LFMC
    df['LC_modis_id'] = np.nan
    df['LC_modis'] = np.nan
       
    tiles_borders = dict() # format: left, right, top, bottom
    for tile in tiles:
        tiles_borders[tile] = list() 

    for tile in tiles:
        print(tile)
        path_to_tile = glob('{}/2020.01.01/*{}*'.format(path_to_modis,tile))[0] #any date is ok for the purpose of defining borders
        hdf = gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band1'.format(path_to_tile))
        geot = hdf.GetGeoTransform()
        x_size = hdf.RasterXSize
        y_size = hdf.RasterYSize
        res = geot[1]

        tiles_borders[tile] = [geot[0], geot[0]+res*x_size, geot[3], geot[3]-res*y_size]

    for tile in tiles:
        print(tile)
        x_min = tiles_borders[tile][0]
        x_max = tiles_borders[tile][1]
        y_min = tiles_borders[tile][3]
        y_max = tiles_borders[tile][2]
        df.loc[(df[x_col_name]>x_min) & (df[x_col_name]<x_max) & (df[y_col_name]>y_min) & (df[y_col_name]<y_max), 'tile'] = tile


    for tile in tiles:
        print(tile)

        dates = sorted(set(df.loc[(df['tile']==tile),args.datecolname]))

        for date in dates:
            # if the dates in the CSV file refers to the start of a fire, it could be beneficial to extract the LFMC value of 8 days prior those dates, 
            # so that it is sure that the reflectance data on which LFMC is based on is not influenced by the fire itself (currently MCD43A4 is a composite of 16 days centered at the 9th day)
            date_time = datetime.strptime(date, '%d/%m/%Y') - timedelta(days=args.lagdays)  

            print(date,'==', datetime.strptime(date, '%d/%m/%Y'), '->',date_time)

            path_to_tile = glob('{}/{}/*{}*'.format(path_to_modis,date_time.strftime('%Y.%m.%d'),tile))[0]
            tile_file = xr.open_dataset(path_to_tile)#, engine='netcdf4')

            tile_file_gdal = gdal.Open('HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band1'.format(path_to_tile))
            geot_tile = tile_file_gdal.GetGeoTransform()

            sub_df = df.loc[(df['tile']==tile) & (df[args.datecolname]==date)].copy()
            
            for i in sub_df.index:
                if args.projection == 'wgs84':
                    lon = sub_df[x_col_name][i]
                    lat = sub_df[y_col_name][i]
                    x, y = transform(LONGLAT_WGS84, MODIS_SINUSOIDAL, lon, lat) 
                
                elif args.projection == 'sinusoidal':
                    x = sub_df[x_col_name][i]
                    y = sub_df[y_col_name][i]

                lfmc_value, veg_type_model, veg_type_modis = get_lfmc(tile, tile_file, date_time, x, y, geot_tile)
                
                df.loc[i,'LFMC'] = lfmc_value
                df.loc[i,'LFMC_date'] = date_time.strftime('%d/%m/%Y')
                df.loc[i,'LC_model_id'] = veg_type_model
                df.loc[i,'LC_model'] = LC_model[veg_type_model]
                df.loc[i,'LC_modis_id'] = veg_type_modis
                df.loc[i,'LC_modis'] = LC_modis[veg_type_modis]


    df.to_csv(args.outputpath)





