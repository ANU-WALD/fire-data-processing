import numpy as np
import argparse
import xarray as xr
import pandas as pd
import netCDF4
from datetime import datetime



def rank_with_deciles(nc_to_rank, variable, variable_long, path_to_deciles, decile_array_name):

    list_rank_arrays = list()

    for date in nc_to_rank.time.data:
        var_array = nc_to_rank.sel(time=date)['{}'.format(variable_long)].data
        month = pd.to_datetime(date).month
        rank_array = var_array.copy() 
        rank_array = np.where(rank_array>0, 10, np.nan) # starts with rank 10, 10th decile, which includes all values. Then rank is subtracted in for loop below

        for decile in reversed(range(10,100,10)): #start from 90, then 80, 70...10
            print(date, variable, 'decile:', decile)
            decile_array = np.load('{}/{}_month{}_percentile{}.npz'.format(path_to_deciles, variable, month, decile))['{}'.format(decile_array_name)]
            rank_array = np.where(var_array<decile_array, rank_array-1, rank_array) #starting point is 10. If <90th percentile, subtract 1 and get 9, if then below 80th get 8.. and so on until 1 for values that are lower than 10th percentile. Nan values are not affected and stay where originally are

        list_rank_arrays.append(rank_array)

    rank_array_3d = np.stack(list_rank_arrays, axis=0)

    return rank_array_3d




def group_deciles(rank_array):
        
        group_array = rank_array.copy() * np.nan
        group_array = np.where(rank_array==1, 1, group_array)
        group_array = np.where(rank_array==2, 1, group_array)
        group_array = np.where(rank_array==3, 2, group_array)
        group_array = np.where(rank_array==4, 2, group_array)
        group_array = np.where(rank_array==5, 3, group_array)
        group_array = np.where(rank_array==6, 3, group_array)
        group_array = np.where(rank_array==7, 4, group_array)
        group_array = np.where(rank_array==8, 4, group_array)
        group_array = np.where(rank_array==9, 5, group_array)
        group_array = np.where(rank_array==10, 5, group_array)


        return group_array




def create_netcdf_mosaic(path_output, nc_to_rank, decile_array, group_array):

    dates = [datetime.utcfromtimestamp(d.astype('O')/1e9) for d in list(nc_to_rank.time.data)]
    lons = list(nc_to_rank.longitude.data)
    lats = list(nc_to_rank.latitude.data)

    with netCDF4.Dataset(path_output, 'w', format='NETCDF4_CLASSIC') as ds:

        t_dim = ds.createDimension("time", len(dates))
        x_dim = ds.createDimension("longitude", len(lons))
        y_dim = ds.createDimension("latitude", len(lats))

        var = ds.createVariable("time", "f8", ("time",))
        var.units = "seconds since 1970-01-01 00:00:00.0"
        var.calendar = "standard"
        var.long_name = "Time, unix time-stamp"
        var.standard_name = "time"
        var[:] = netCDF4.date2num(dates, units="seconds since 1970-01-01 00:00:00.0", calendar="standard")

        var = ds.createVariable("longitude", "f8", ("longitude",))
        var.units = "degrees"
        var.long_name = "longitude"
        var.standard_name = "longitude"
        var[:] = lons
        
        var = ds.createVariable("latitude", "f8", ("latitude",))
        var.units = "degrees"
        var.long_name = "latitude"
        var.standard_name = "latitude"
        var[:] = lats

        var = ds.createVariable('decile_values', np.int8, ('time', 'latitude', 'longitude'), fill_value=111, zlib=True, complevel=9)
        var.units = 'int8'
        var.long_name = 'deciles'
        var[:] = decile_array
        
        var = ds.createVariable('decile_groups', np.int8, ('time', 'latitude', 'longitude'), fill_value=111, zlib=True, complevel=9)
        var.units = 'int8'
        var.long_name = 'decile groups'
        var[:] = group_array








if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="""ranking using deciles arrays""")
    parser.add_argument('-decfolder', '--decilefolder', type=str, required=True, help="path to folder with input decile arrays")
    parser.add_argument('-mosfolder', '--mosaicfolder', type=str, required=True, help="path to folder with input netcf flam and fmc")
    parser.add_argument('-var', '--variable', type=str, required=True, help="'fmc' 'flam' or 'both'")
    parser.add_argument('-ystart', '--yearstart', type=str, required=True, help="first year of interest")
    parser.add_argument('-yend', '--yearend', type=str, required=True, help="last year of interest")
    parser.add_argument('-outfolder', '--outputfolder', required=True, type=str, help="path to folder where to save output")
    args = parser.parse_args()


    # example for running script
    # /g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_rank_with_deciles.py -decfolder /g/data/ub8/au/FMC/intermediary_files/deciles_arrays -mosfolder /g/data/ub8/au/FMC/mosaics -var both -ystart 2001 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats
 


    for year in range(int(args.yearstart), int(args.yearend)+1):
        print('year:',year)

        if args.variable == 'both':
            for var, var_long in zip(['fmc', 'flam'], ['lfmc_median','flammability']):
                nc = xr.open_dataset('{}/{}_c6_{}.nc'.format(args.mosaicfolder, var, year))

                rank_array_3d = rank_with_deciles(nc, var, var_long, args.decilefolder, 'percentile')
                group_array_3d = group_deciles(rank_array_3d)

                rank_array_3d[np.isnan(rank_array_3d)] = 111
                rank_array_3d = rank_array_3d.astype(int)

                group_array_3d[np.isnan(group_array_3d)] = 111
                group_array_3d = group_array_3d.astype(int)

                output_file = '{}/{}_c6_{}_dc.nc'.format(args.outputfolder,var,year)

                create_netcdf_mosaic(output_file, nc, rank_array_3d, group_array_3d)


        else:
            if args.variable == 'flam':
                var_long = 'flammability'
            elif args.variable == 'fmc':
                var_long = 'lfmc_median'

            nc = xr.open_dataset('{}/{}_c6_{}.nc'.format(args.mosaicfolder, args.variable, year))

            rank_array_3d = rank_with_deciles(nc, args.variable, var_long, args.decilefolder, 'percentile')
            group_array_3d = group_deciles(rank_array_3d)

            rank_array_3d[np.isnan(rank_array_3d)] = 111
            rank_array_3d = rank_array_3d.astype(int)

            group_array_3d[np.isnan(group_array_3d)] = 111
            group_array_3d = group_array_3d.astype(int)

            output_file = '{}/{}_c6_{}_dc.nc'.format(args.outputfolder,args.variable,year)

            create_netcdf_mosaic(output_file, nc, rank_array_3d, group_array_3d)

    




