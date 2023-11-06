import xarray as xr
from glob import glob
import argparse

def compress_and_save(path_original, path_output, product):

    nc = xr.open_dataset(path_original)

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




if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="""Compress AFMS NetCDF files argument parser""")
    parser.add_argument('-y', '--year', type=str, required=True, help="Year of files to compress")
    parser.add_argument('-type', '--filetype', type=str,required=True, help="Either tile or mosaic")
    parser.add_argument('-t', '--tile',type=str, help="Tile to compress")
    parser.add_argument('-var', '--variable', type=str,required=True, help="Either fmc or flam or both")
    parser.add_argument('-in', '--input', type=str,required=True,  help="Full path to non compressed files.")
    parser.add_argument('-out', '--output', type=str, required=True, help="Full path to destination.")
    args = parser.parse_args()

    # example for running script
    # /g/data/xc0/software/conda-envs/rs3/bin/python compress_nc_files.py -y 2001 -type tile -t h30v11 -var fmc -in /g/data/ub8/au/FMC/tiles -out /g/data/ub8/au/FMC/tiles_compressed
    # /g/data/xc0/software/conda-envs/rs3/bin/python compress_nc_files.py -y 2001 -type mosaic -var fmc -in /g/data/ub8/au/FMC/mosaics -out /g/data/ub8/au/FMC/mosaics_compressed
 
    #tiles
    if args.filetype == 'tile':
        if args.variable == 'both':
            for var in ['flam', 'fmc']:

                path_original = '{}/{}_c6_{}_{}.nc'.format(args.input,var,args.year,args.tile)
                path_output = '{}/{}_c6_{}_{}.nc'.format(args.output,var,args.year,args.tile)

                if not glob(path_output):
                    print(path_output.split('/')[-1])
                    compress_and_save(path_original, path_output, var)

        else:
            var = args.variable

            path_original = '{}/{}_c6_{}_{}.nc'.format(args.input,var,args.year,args.tile)
            path_output = '{}/{}_c6_{}_{}.nc'.format(args.output,var,args.year,args.tile)

            if not glob(path_output):
                print(path_output.split('/')[-1])
                compress_and_save(path_original, path_output, var)


    #mosaics
    elif args.filetype == 'mosaic':
        if args.variable == 'both':
            for var in ['flam', 'fmc']:

                path_original = '{}/{}_c6_{}.nc'.format(args.input,var,args.year) 
                path_output = '{}/{}_c6_{}.nc'.format(args.output,var,args.year)

                if not glob(path_output):
                    print(path_output.split('/')[-1])
                    compress_and_save(path_original, path_output, var)

        else:
            var = args.variable

            path_original = '{}/{}_c6_{}.nc'.format(args.input,var,args.year) 
            path_output = '{}/{}_c6_{}.nc'.format(args.output,var,args.year)

            if not glob(path_output):
                print(path_output.split('/')[-1])
                compress_and_save(path_original, path_output, var)




