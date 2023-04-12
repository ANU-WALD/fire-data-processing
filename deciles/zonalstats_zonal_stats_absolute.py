import numpy as np
import argparse
import xarray as xr
import os.path
import glob
import netCDF4
import uuid
from datetime import datetime
import shutil



def get_stack_dates(file_path):

    if os.path.isfile(file_path):
        ds = xr.open_dataset(file_path)
        return ds.time.data
        
    return []




def get_veg_mask(year, vegmask_folder_path):

    list_mask_paths = glob.glob('{}/veg_mask_*.npz'.format(vegmask_folder_path))
    list_mask_years = [int(path[-8:-4]) for path in list_mask_paths]
    max_year = np.nanmax(list_mask_years)

    if year <= max_year: #use actual year of interest
        mask_array = np.load('{}/veg_mask_{}.npz'.format(vegmask_folder_path, year))['veg_mask']

    elif year > max_year: #use the latest year available
        mask_array = np.load('{}/veg_mask_{}.npz'.format(vegmask_folder_path, max_year))['veg_mask']

    return mask_array




def pack_netcdf(var_netcdf, var_name, date, areas_mask, veg_mask, temp_file):

    if var_name == 'fmc':
        var_name = 'lfmc_median'
    elif var_name == 'flam':
        var_name = 'flammability'

    var_array = var_netcdf.sel(time=date)['{}'.format(var_name)].data

    areas_id = np.unique(areas_mask) 
    areas_id = areas_id[areas_id != 0].copy() #exclude 0 which is fill value
    areas_id = sorted(areas_id)


    stats_dict = dict() #create empty dictonary to populate with stats data
    for stat in ['avg','coverage','max','min']:
        for code in ['','_1','_2','_3']:
            stats_dict['{}{}'.format(stat,code)] = list()

    for id in areas_id:

        area_masked_array = np.where(areas_mask==id, var_array, np.nan)
        
        stats_dict['coverage'].append(np.round(np.nansum(~np.isnan(area_masked_array)) / np.nansum(np.where(areas_mask==id,1,0)) * 100., decimals=1))
        stats_dict['avg'].append(np.round(np.nanmean(area_masked_array), decimals=2))
        stats_dict['max'].append(np.nanmax(area_masked_array))
        stats_dict['min'].append(np.nanmin(area_masked_array))

        for veg_type in [1,2,3]: # 1->grass, 2->shurb, 3->forest

            veg_masked_array = np.where(veg_mask==veg_type, area_masked_array, np.nan)

            stats_dict['coverage_{}'.format(veg_type)].append(np.round(np.nansum(~np.isnan(veg_masked_array)) / np.nansum(np.where(areas_mask==id,1,0)) * 100., decimals=1))
            stats_dict['avg_{}'.format(veg_type)].append(np.round(np.nanmean(veg_masked_array), decimals=2))
            stats_dict['max_{}'.format(veg_type)].append(np.nanmax(veg_masked_array))
            stats_dict['min_{}'.format(veg_type)].append(np.nanmin(veg_masked_array))


    with netCDF4.Dataset(temp_file, 'w', format='NETCDF4_CLASSIC') as ds:

        t_dim = ds.createDimension('time', 1)
        id_dim = ds.createDimension('plg_id', len(areas_id))

        var = ds.createVariable('time', 'f8', ('time',))
        var.units = 'seconds since 1970-01-01 00:00:00.0'
        var.calendar = 'standard'
        var.long_name = 'Time, unix time-stamp'
        var.standard_name = 'time'
        var[:] = netCDF4.date2num([datetime.utcfromtimestamp(date.astype('O')/1e9)], units='seconds since 1970-01-01 00:00:00.0', calendar='standard')

        var = ds.createVariable('plg_id', 'i4', ('plg_id',))
        var.units = 'Cat'
        var.long_name = 'Area ID'
        var.standard_name = 'plg_id'
        var[:] = areas_id

        for stat in ['avg','coverage','max','min']:
            for code in ['','_1','_2','_3']:

                var = ds.createVariable('{}{}'.format(stat,code), 'f4', ('time', 'plg_id'))
                var.long_name = '{}{}'.format(stat,code)
                array_from_dict = np.asarray(stats_dict['{}{}'.format(stat,code)])
                var[:] = array_from_dict[None,...]




def update_netcdf(output_dest, var_netcdf, var_name, date, areas_mask, veg_mask, temp_dest_folder):
    
    temp_file = os.path.join(temp_dest_folder, uuid.uuid4().hex + '.nc')

    pack_netcdf(var_netcdf, var_name, date, areas_mask, veg_mask, temp_file)

    if not os.path.isfile(output_dest):
        shutil.move(temp_file, output_dest)
    else:
        temp_file2 = os.path.join(temp_dest_folder, uuid.uuid4().hex + '.nc')
        os.system('cdo mergetime {} {} {}'.format(temp_file, output_dest, temp_file2))
        os.remove(temp_file)
        shutil.move(temp_file2, output_dest)





if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="""create absolute zonal stats using shapefiles""")
    parser.add_argument('-mosfolder', '--mosaicfolder', type=str, required=True, help="path to folder with input fmc and flam mosaics")
    parser.add_argument('-vegmaskfolder', '--vegetationmaskfolder', type=str, required=True, help="path to folder with vegetation masks arrays")
    parser.add_argument('-areafolder', '--areafilefolder', type=str, required=True, help="path to folder containing folders of FWA and LGA")
    parser.add_argument('-area', '--areaclassification', type=str, required=True, help="'fwa' 'lga' or 'both")
    parser.add_argument('-var', '--variable', type=str, required=True, help="'fmc' 'flam' or 'both'")
    parser.add_argument('-ystart', '--yearstart', type=str, required=True, help="first year of interest")
    parser.add_argument('-yend', '--yearend', type=str, required=True, help="last year of interest")
    parser.add_argument('-outfolder', '--outputfolder', required=True, type=str, help="path to folder where to save output")
    parser.add_argument('-tmpfolder', '--temporaryfolder', required=True, type=str, help="path to folder where to save temporary files")
    args = parser.parse_args()

    # example for running script
    # module load cdo
    # /g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_zonal_stats_absolute.py -mosfolder /g/data/ub8/au/FMC/mosaics -vegmaskfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask -areafolder /g/data/ub8/au/FMC/intermediary_files/areal_classifications -area both -var both -ystart 2001 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats/zonal_stats/new -tmpfolder /g/data/ub8/au/FMC/tmp 
    
    y_start = int(args.yearstart)
    y_end = int(args.yearend)

    for year in range(y_start, y_end+1):
        veg_mask = get_veg_mask(year, args.vegetationmaskfolder)

        if args.variable == 'both':

            for var in ['fmc','flam']:
                var_ds = xr.open_dataset('{}/{}_c6_{}.nc'.format(args.mosaicfolder, var, year))

                if args.areaclassification == 'both':
                    for area in ['fwa','lga']:
                        areas_mask = np.load('{0}/{1}/{1}.npz'.format(args.areafilefolder, area))['{}'.format(area)]
                        output_path = '{}/{}_{}_nc_zonal_stat.nc'.format(args.outputfolder, area.upper(), var)
                        output_dates = get_stack_dates(output_path)
                        for date in var_ds.time.data:
                            print(date)
                            if date not in output_dates:
                                update_netcdf(output_path, var_ds, var, date, areas_mask, veg_mask, args.temporaryfolder)
         
                else:
                    area = args.areaclassification
                    areas_mask = np.load('{0}/{1}/{1}.npz'.format(args.areafilefolder, area))['{}'.format(area)]
                    output_path = '{}/{}_{}_nc_zonal_stat.nc'.format(args.outputfolder, area.upper(), var)
                    output_dates = get_stack_dates(output_path)
                    for date in var_ds.time.data:
                        print(date)
                        if date not in output_dates:
                            update_netcdf(output_path, var_ds, var, date, areas_mask, veg_mask, args.temporaryfolder)

        else:
            var = args.variable
            var_ds = xr.open_dataset('{}/{}_c6_{}.nc'.format(args.mosaicfolder, var, year))

            if args.areaclassification == 'both':
                for area in ['fwa','lga']:
                    areas_mask = np.load('{0}/{1}/{1}.npz'.format(args.areafilefolder, area))['{}'.format(area)]
                    output_path = '{}/{}_{}_nc_zonal_stat.nc'.format(args.outputfolder, area.upper(), var)
                    output_dates = get_stack_dates(output_path)
                    for date in var_ds.time.data:
                        print(date)
                        if date not in output_dates:
                            update_netcdf(output_path, var_ds, var, date, areas_mask, veg_mask, args.temporaryfolder)
                            
            else:
                area = args.areaclassification
                areas_mask = np.load('{0}/{1}/{1}.npz'.format(args.areafilefolder, area))['{}'.format(area)]
                output_path = '{}/{}_{}_nc_zonal_stat.nc'.format(args.outputfolder, area.upper(), var)
                output_dates = get_stack_dates(output_path)
                for date in var_ds.time.data:
                    print(date)
                    if date not in output_dates:
                        update_netcdf(output_path, var_ds, var, date, areas_mask, veg_mask, args.temporaryfolder)


