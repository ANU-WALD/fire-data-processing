
# DS = xr.open_dataset(in_path_file)
# DS['flammability'][:, :, :] = 1.0
# print(DS.flammability.dims)

# DS_deciles = copy(DS)
# DS_deciles.rename(name_dict={'flammability': 'flammability_deciles'}, inplace=True)
# DS_deciles.flammability_deciles = np.nan
# print(DS_deciles.flammability_deciles[])
# print(DS_deciles)

# exit()
# print(DS.dims)
# print(DS.coords)
# print(DS.variables)
# print(DS.var)

# da = DS.flammability
# print(da.shape)

# cnt = 0
# for lat in range(0, 6800+1, 1000):
#     for lon in range(0, 8200+1, 1000):
#         cnt += 1
#         print(lat, lon, cnt)
# exit()

# da_tile = da[:, 0:10, 0:10]
# p = da_tile.quantile(q=0.1, dim='time')
# print(p)

# DS_decile = DS.copy(deep=True,)
# DS.assign()

# p = DS.flammability.quantile(q=0.1, dim='time')
# p = DS.flammability.quantile(q=0.1, dim='time')


# cmd_cdo = '/bin/bash -c "module load cdo; cdo fldpctl,90 ' + in_path_file + ' ' + out_path_file + '"'
# print(cmd_cdo)
# os.system(cmd_cdo)

# NOTE: above method doesn't work as it returns single value. To use numpy.
# read the file, convert to numpy and calc percentiles and store as NC
# check if to read all data, use tiling if not possible