import os

#LGA11aAust
#manually converted projection of this shp file to WGS 84 in QGIS
#then the following command creates a NetCDF file to be used by 04_zonal_statistics_deciles.py script
 
print('LGA...')

# create nc of the plgs shp file if does not exist. This works for LGA11aAust for now
nc_plg_path_file = '/g/data/ub8/au/FMC/calc_deciles/data/LGAs/LGA11aAust.nc'
if not os.path.exists(nc_plg_path_file):
    shp_plg_path_file = '/g/data/ub8/au/FMC/calc_deciles/data/LGAs/LGA11aAust_wgs84.shp'
    shp_layer = 'LGA11aAust_wgs84'
    att_filed = 'LGA_CODE11'
    cmd_rasterize = 'gdal_rasterize -l' + ' ' + shp_layer + ' -a ' + att_filed + ' -tr 0.005 0.005 -a_nodata -9999.0 -te 112.9975 -43.9975 153.9975 -9.9975 -ot Float32 -of netCDF -co WRITE_BOTTOMUP=NO ' + shp_plg_path_file + ' ' + nc_plg_path_file
    os.system(cmd_rasterize)

#Fire Weather
#manually converted projection of this shp to WGS 84 in QGIS
#added a new field (plg_id) to the table and set it as row number using @row_number in table in QGIS

#note:
#2019.10.18
#used version 2 as received from Marta following his meeting with website users

print('FWA...')

nc_plg_path_file = '/g/data/ub8/au/FMC/calc_deciles/data/FWA/gfe_fire_weather.nc'
if not os.path.exists(nc_plg_path_file):
    shp_plg_path_file = '/g/data/ub8/au/FMC/calc_deciles/data/FWA/gfe_fire_weather_wgs_84_v2.shp'
    shp_layer = 'gfe_fire_weather_wgs_84_v2'
    att_filed = 'plg_id'
    cmd_rasterize = 'gdal_rasterize -l' + ' ' + shp_layer + ' -a ' + att_filed + ' -tr 0.005 0.005 -a_nodata -9999.0 -te 112.9975 -43.9975 153.9975 -9.9975 -ot Float32 -of netCDF -co WRITE_BOTTOMUP=NO ' + shp_plg_path_file + ' ' + nc_plg_path_file
    print(cmd_rasterize)
    os.system(cmd_rasterize)

print('aus_states...')

nc_plg_path_file = '/g/data/ub8/au/FMC/calc_deciles/data/States/aus_states.nc'
if not os.path.exists(nc_plg_path_file):
    shp_plg_path_file = '/g/data/ub8/au/FMC/calc_deciles/data/States/aus_states_WGS_84.shp'
    shp_layer = 'aus_states_WGS_84'
    att_filed = 'STATE_CODE'
    cmd_rasterize = 'gdal_rasterize -l' + ' ' + shp_layer + ' -a ' + att_filed + ' -tr 0.005 0.005 -a_nodata -9999.0 -te 112.9975 -43.9975 153.9975 -9.9975 -ot Float32 -of netCDF -co WRITE_BOTTOMUP=NO ' + shp_plg_path_file + ' ' + nc_plg_path_file
    print(cmd_rasterize)
    # os.system(cmd_rasterize)
