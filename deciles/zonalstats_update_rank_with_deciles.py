import numpy as np
import argparse
import xarray as xr
import pandas as pd
import netCDF4
from datetime import datetime
import os.path
import uuid
import shutil




def get_stack_dates(file_path):

    if os.path.isfile(file_path):
        ds = xr.open_dataset(file_path)
        return ds.time.data
        
    return []




def rank_with_deciles(array_to_rank, month, variable, path_to_deciles, decile_array_name):

    rank_array = array_to_rank.copy() 
    rank_array = np.where(rank_array>0, 10, np.nan) # starts with rank 10, 10th decile, which includes all values. Then rank is subtracted in for loop below

    for decile in reversed(range(10,100,10)): #start from 90, then 80, 70...10
        print(variable, 'decile:', decile)
        decile_array = np.load('{}/{}_month{}_percentile{}.npz'.format(path_to_deciles, variable, month, decile))['{}'.format(decile_array_name)]
        rank_array = np.where(array_to_rank<decile_array, rank_array-1, rank_array) #starting point is 10. If <90th percentile, subtract 1 and get 9, if then below 80th get 8.. and so on until 1 for values that are lower than 10th percentile. Nan values are not affected and stay where originally are

    return rank_array




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




def pack_netcdf(path_output, nc_template, decile_array, group_array):

    lons = list(nc_template.longitude.data)
    lats = list(nc_template.latitude.data)

    with netCDF4.Dataset(path_output, 'w', format='NETCDF4_CLASSIC') as ds:

        t_dim = ds.createDimension("time", 1)
        x_dim = ds.createDimension("longitude", len(lons))
        y_dim = ds.createDimension("latitude", len(lats))

        var = ds.createVariable("time", "f8", ("time",))
        var.units = "seconds since 1970-01-01 00:00:00.0"
        var.calendar = "standard"
        var.long_name = "Time, unix time-stamp"
        var.standard_name = "time"
        var[:] = netCDF4.date2num([datetime.utcfromtimestamp(date.astype('O')/1e9)], units="seconds since 1970-01-01 00:00:00.0", calendar="standard")

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

        var = ds.createVariable('decile_values', np.int8, ('time', 'latitude', 'longitude'), fill_value=111)
        var.units = 'int8'
        var.long_name = 'deciles'
        var[:] = decile_array[None,...]
        
        var = ds.createVariable('decile_groups', np.int8, ('time', 'latitude', 'longitude'), fill_value=111)
        var.units = 'int8'
        var.long_name = 'decile groups'
        var[:] = group_array[None,...]




def update_netcdf(output_dest, nc_template, decile_array, group_array, temp_dest_folder):
    
    temp_file = os.path.join(temp_dest_folder, uuid.uuid4().hex + '.nc')

    pack_netcdf(temp_file, nc_template, decile_array, group_array)

    if not os.path.isfile(output_dest):
        shutil.move(temp_file, output_dest)
    else:
        temp_file2 = os.path.join(temp_dest_folder, uuid.uuid4().hex + '.nc')
        os.system('cdo mergetime {} {} {}'.format(temp_file, output_dest, temp_file2))
        os.remove(temp_file)
        shutil.move(temp_file2, output_dest)





if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="""ranking using deciles arrays""")
    parser.add_argument('-decfolder', '--decilefolder', type=str, required=True, help="path to folder with input decile arrays")
    parser.add_argument('-mosfolder', '--mosaicfolder', type=str, required=True, help="path to folder with input netcf flam and fmc")
    parser.add_argument('-var', '--variable', type=str, required=True, help="'fmc' 'flam' or 'both'")
    parser.add_argument('-ystart', '--yearstart', type=str, required=True, help="first year of interest")
    parser.add_argument('-yend', '--yearend', type=str, required=True, help="last year of interest")
    parser.add_argument('-outfolder', '--outputfolder', required=True, type=str, help="path to folder where to save output")
    parser.add_argument('-tmpfolder', '--temporaryfolder', required=True, type=str, help="path to folder where to save temporary files")
    args = parser.parse_args()


    # example for running script
    # module load cdo
    # /g/data/xc0/software/conda-envs/rs3/bin/python /g/data/xc0/user/scortechini/github/fire-data-processing/deciles/zonalstats_update_rank_with_deciles.py -decfolder /g/data/ub8/au/FMC/intermediary_files/deciles_arrays -mosfolder /g/data/ub8/au/FMC/mosaics -var both -ystart 2023 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats -tmpfolder /g/data/ub8/au/FMC/tmp
 
    y_start = int(args.yearstart)
    y_end = int(args.yearend)

    for year in range(y_start, y_end+1):
        print('year:',year)

        if args.variable == 'both':
            for var, var_long in zip(['fmc', 'flam'], ['lfmc_median','flammability']):

                output_file = '{}/{}_c6_{}_dc.nc'.format(args.outputfolder,var,year)
                output_dates = get_stack_dates(output_file)

                nc = xr.open_dataset('{}/{}_c6_{}.nc'.format(args.mosaicfolder, var, year))

                for date in nc.time.data:
                    print(date)
                    if date not in output_dates:
                        var_array = nc.sel(time=date)['{}'.format(var_long)].data
                        month = pd.to_datetime(date).month

                        rank_array = rank_with_deciles(var_array, month, var, args.decilefolder, 'percentile')
                        rank_array[np.isnan(rank_array)] = 111
                        rank_array = rank_array.astype(int)

                        group_array = group_deciles(rank_array)
                        group_array[np.isnan(group_array)] = 111
                        group_array = group_array.astype(int)

                        update_netcdf(output_file, nc, rank_array, group_array, args.temporaryfolder) 


        else:
            var = args.variable
            if var == 'flam':
                var_long = 'flammability'
            elif var == 'fmc':
                var_long = 'lfmc_median'

            output_file = '{}/{}_c6_{}_dc.nc'.format(args.outputfolder,var,year)
            output_dates = get_stack_dates(output_file)

            nc = xr.open_dataset('{}/{}_c6_{}.nc'.format(args.mosaicfolder, var, year))

            for date in nc.time.data:
                print(date)
                if date not in output_dates:
                    var_array = nc.sel(time=date)['{}'.format(var_long)].data
                    month = pd.to_datetime(date).month

                    rank_array = rank_with_deciles(var_array, month, var, args.decilefolder, 'percentile')
                    rank_array[np.isnan(rank_array)] = 111
                    rank_array = rank_array.astype(int)

                    group_array = group_deciles(rank_array)
                    group_array[np.isnan(group_array)] = 111
                    group_array = group_array.astype(int)

                    update_netcdf(output_file, nc, rank_array, group_array, args.temporaryfolder) 





