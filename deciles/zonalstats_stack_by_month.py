import xarray as xr
import numpy as np
import argparse
import pandas as pd

def monthly_stack(folder_path, month, year_start, year_end, var_filename, var_infile):

    list_arrays = list()

    for year in range(year_start, year_end+1):
        print(year, month)
        nc = xr.open_dataset('{}/{}_c6_{}.nc'.format(folder_path, var_filename,year))

        for date in nc.time.data:
            month_date = pd.to_datetime(date).month

            if month_date == month:
                sub_nc = nc.sel(time=date)
                array = sub_nc['{}'.format(var_infile)].data
                list_arrays.append(array)

    array_3d = np.dstack(list_arrays)

    return array_3d




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""monthly stacks argument parser""")
    parser.add_argument('-infolder', '--inputfolder', type=str, required=True, help="path to folder with input mosaics")
    parser.add_argument('-var', '--variable', type=str, required=True, help="'fmc' 'flam' or 'both'")
    parser.add_argument('-ystart', '--yearstart', type=str, required=True, help="first year of timeseries")
    parser.add_argument('-yend', '--yearend', type=str, required=True, help="last year of timeseries")
    parser.add_argument('-outfolder', '--outputfolder', required=True, type=str, help="path to folder where to save output")
    args = parser.parse_args()

    # example for running script
    # /g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_stack_by_month.py -infolder /g/data/ub8/au/FMC/mosaics -var both -ystart 2001 -yend 2022 -outfolder /g/data/ub8/au/FMC/intermediary_files/stack_by_month_2001_2022


    in_folder_path = args.inputfolder
    out_folder_path = args.outputfolder

    start = int(args.yearstart)
    end = int(args.yearend)

    var = args.variable

    if var == 'fmc':
        for month in range(1,13):
            month_stack = monthly_stack(in_folder_path, month, start, end, var, 'lfmc_median')
            np.savez_compressed('{}/fmc_month{}.npz'.format(out_folder_path,month), fmc=month_stack)
            del month_stack
            
    elif args.variable == 'flam':
        for month in range(1,13):
            month_stack = monthly_stack(in_folder_path, month, start, end, var, 'flammability')
            np.savez_compressed('{}/flam_month{}.npz'.format(out_folder_path,month), flam=month_stack)
            del month_stack

    elif args.variable == 'both':
        for month in range(1,13):
            fmc_month_stack = monthly_stack(in_folder_path, month, start, end, 'fmc', 'lfmc_median')
            np.savez_compressed('{}/fmc_month{}.npz'.format(out_folder_path,month), fmc=fmc_month_stack)
            del fmc_month_stack

            flam_month_stack = monthly_stack(in_folder_path, month, start, end, 'flam', 'flammability')
            np.savez_compressed('{}/flam_month{}.npz'.format(out_folder_path,month), flam=flam_month_stack)
            del flam_month_stack





