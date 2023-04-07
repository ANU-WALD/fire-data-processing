import os
import netCDF4 as nc


def copy_nc_exclude(src_path_file, dst_path_file, exclude_dims, exclude_vars):
    if os.path.exists(dst_path_file):
        os.remove(dst_path_file)

    with nc.Dataset(src_path_file) as src, nc.Dataset(dst_path_file, "w", format='NETCDF4_CLASSIC') as dst:
        # copy global attributes all at once via dictionary
        dst.setncatts(src.__dict__)
        # copy dimensions
        for name, dimension in src.dimensions.items():
            print(name)
            if name not in exclude_dims:
                dst.createDimension(
                    name, (len(dimension) if not dimension.isunlimited() else None))
        print('---------------------')
        # copy all file data except for the excluded
        for name, variable in src.variables.items():
            print(name)
            if name not in exclude_vars:
                print(name)
                x = dst.createVariable(name, variable.datatype, variable.dimensions)
                dst[name][:] = src[name][:]
                # copy variable attributes all at once via dictionary
                dst[name].setncatts(src[name].__dict__)


def copy_nc_include(src_path_file, dst_path_file, include_dims, include_vars):
    if os.path.exists(dst_path_file):
        os.remove(dst_path_file)

    with nc.Dataset(src_path_file) as src, nc.Dataset(dst_path_file, "w", format='NETCDF4_CLASSIC') as dst:
        # copy global attributes all at once via dictionary
        dst.setncatts(src.__dict__)
        # copy dimensions
        for name, dimension in src.dimensions.items():
            print(name)
            if name in include_dims:
                dst.createDimension(
                    name, (len(dimension) if not dimension.isunlimited() else None))
        print('---------------------')
        # copy all file data except for the excluded
        for name, variable in src.variables.items():
            print(name)
            if name in include_vars:
                x = dst.createVariable(name, variable.datatype, variable.dimensions)
                dst[name][:] = src[name][:]
                # copy variable attributes all at once via dictionary
                dst[name].setncatts(src[name].__dict__)
