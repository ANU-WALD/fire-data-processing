import xarray as xr
from glob import glob

def compress_and_save(path_original, path_output, product):

    nc = xr.load_dataset(path_original)

    comp = {'zlib':True,'complevel':9}

    if product == 'flam':
        var_comp = {'flammability':comp,
                    'quality_mask':comp,
                    'anomaly':comp}

    elif product == 'fmc':
        var_comp = {'lfmc_median':comp,
                    'quality_mask':comp,
                    'lfmc_stdv':comp}


    nc.to_netcdf(path_output, encoding=var_comp)

    return None



au_tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", 
            "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", 
            "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", 
            "h32v10", "h32v11"]


if __name__ == '__main__':

    year_start = 2023
    year_end = 2023 #inclusive
    
    #tiles
    for var in ['flam', 'fmc']:
        for year in range(year_start,year_end+1):
            for tile in au_tiles:

                path_original = '/g/data/ub8/au/FMC/tiles/{}_c6_{}_{}.nc'.format(var,year,tile)
                path_output = '/g/data/ub8/au/FMC/tmp/{}_c6_{}_{}.nc'.format(var,year,tile)

                if not glob(path_output):
                    print(path_output.split('/')[-1])
                    compress_and_save(path_original, path_output, var)


    #mosaics
    for var in ['flam', 'fmc']:
        for year in range(year_start,year_end+1):

            path_original = '/g/data/ub8/au/FMC/mosaics/{}_c6_{}.nc'.format(var,year) 
            path_output = '/g/data/ub8/au/FMC/tmp/{}_c6_{}.nc'.format(var,year)

            if not glob(path_output):
                print(path_output.split('/')[-1])
                compress_and_save(path_original, path_output, var)




