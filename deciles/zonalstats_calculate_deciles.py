import numpy as np
import argparse


def compute_percentile(folder_path, month, var, percentile):
    '''compute percentile over time axis (z axis) using closest observation method'''

    array_3d = np.load('{}/{}_month{}.npz'.format(folder_path, var, month))['{}'.format(var)]
    #output = np.nanpercentile(array_3d, percentile, axis=2, method='closest_observation')
    output = np.nanpercentile(array_3d, percentile, axis=2, interpolation='nearest') #for older versions of numpy
    del array_3d

    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""calculation monthly deciles""")
    parser.add_argument('-infolder', '--inputfolder', type=str, required=True, help="path to folder with input mosaics")
    parser.add_argument('-var', '--variable', type=str, required=True, help="'fmc' 'flam' or 'both'")
    parser.add_argument('-month', '--month', type=str, required=True, help="single month of the year as integer or 'all'")
    parser.add_argument('-outfolder', '--outputfolder', required=True, type=str, help="path to folder where to save output")
    args = parser.parse_args()

    # example for running script
    # /g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_calculate_deciles.py -infolder /g/data/ub8/au/FMC/intermediary_files/stack_by_month_2001_2022 -var both -month all -outfolder /g/data/ub8/au/FMC/intermediary_files/deciles_arrays


    in_folder_path = args.inputfolder
    out_folder_path = args.outputfolder

    if args.month == 'all':
        if args.variable == 'both':
            for var in ['fmc','flam']:
                for month in range(1,13):
                    for percentile in range(10,100,10):
                        perc_array = compute_percentile(in_folder_path, month, var, percentile)
                        np.savez_compressed('{}/{}_month{}_percentile{}.npz'.format(out_folder_path,var,month, percentile), percentile=perc_array)
                        del perc_array
        
        else:
            for month in range(1,13):
                for percentile in range(10,100,10):
                    perc_array = compute_percentile(in_folder_path, month, args.variable, percentile)
                    np.savez_compressed('{}/{}_month{}_percentile{}.npz'.format(out_folder_path, args.variable, month, percentile), percentile=perc_array)
                    del perc_array

    
    else:
        if args.variable == 'both':
            for var in ['fmc','flam']:
                for percentile in range(10,100,10):
                    perc_array = compute_percentile(in_folder_path, args.month, var, percentile)
                    np.savez_compressed('{}/{}_month{}_percentile{}.npz'.format(out_folder_path, var,args.month, percentile), percentile=perc_array)
                    del perc_array

        else:
            for percentile in range(10,100,10):
                perc_array = compute_percentile(in_folder_path, args.month, args.variable, percentile)
                np.savez_compressed('{}/{}_month{}_percentile{}.npz'.format(out_folder_path, args.variable, args.month, percentile), percentile=perc_array)
                del perc_array


    




