import numpy as np
import argparse
from glob import glob
from datetime import datetime
from osgeo import gdal 


def compose_veg_mask_mosaic(year, mask_path, tiles_list, forest_id, shrub_id, grass_id, allrest_id):
    print(year)

    tile_size = 2400
    
    lat_max = -10.
    lat_min = -44.
    lon_max = 154.
    lon_min = 113.
    res = 0.005

    x_size = int((lon_max - lon_min)/res)
    y_size = int((lat_max - lat_min)/res)
    
    geot = [lon_min - res/2, res, 0., lat_max + res/2, 0., -1*res] #gdal geotransform indicate top left corner, not the coord of centre of top left pixel like netcdf
    wgs84_wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    
    src = gdal.GetDriverByName('MEM').Create('', tile_size, tile_size, 1, gdal.GDT_Byte,) #GDT_Byte is 8 bit unsigned integer

    dst = gdal.GetDriverByName('MEM').Create('', x_size, y_size, 1, gdal.GDT_Byte,) #mosaic
    dst.GetRasterBand(1).WriteArray(np.zeros((y_size, x_size), dtype=np.uint8))
    dst.SetGeoTransform(geot)
    dst.SetProjection(wgs84_wkt)

    for tile in tiles_list:
        print(tile)
        masks = glob("{0}/{1}.01.01/MCD12Q1.A{1}001.{2}.061.*.hdf".format(mask_path, year, tile))
        if len(masks) != 1:
            return None
        mask_tile = gdal.Open('HDF4_EOS:EOS_GRID:"{}":MCD12Q1:LC_Type1'.format(masks[0]))

        # Reccomended categories: 1=Grass 2=Shrub 3=Forest 0=No fuel
        veg_mask = mask_tile.ReadAsArray()
        veg_mask[veg_mask == 1] = forest_id # Evergreen Needleleaf Forests: dominated by evergreen conifer trees (canopy >2m). Tree cover >60%.
        veg_mask[veg_mask == 2] = forest_id # Evergreen Broadleaf Forests: dominated by evergreen broadleaf and palmate trees (canopy >2m). Tree cover >60%.
        veg_mask[veg_mask == 3] = forest_id # Deciduous Needleleaf Forests: dominated by deciduous needleleaf (larch) trees (canopy >2m). Tree cover >60%.
        veg_mask[veg_mask == 4] = forest_id # Deciduous Broadleaf Forests: dominated by deciduous broadleaf trees (canopy >2m). Tree cover >60%.
        veg_mask[veg_mask == 5] = forest_id # Mixed Forests: dominated by neither deciduous nor evergreen (40-60% of each) tree type (canopy >2m). Tree cover >60%.
        veg_mask[veg_mask == 6] = shrub_id # Closed Shrublands: dominated by woody perennials (1-2m height) >60% cover.
        veg_mask[veg_mask == 7] = shrub_id # Open Shrublands: dominated by woody perennials (1-2m height) 10-60% cover.
        veg_mask[veg_mask == 8] = forest_id # Woody Savannas: tree cover 30-60% (canopy >2m).
        veg_mask[veg_mask == 9] = forest_id # Savannas: tree cover 10-30% (canopy >2m).
        veg_mask[veg_mask == 10] = grass_id # Grasslands: dominated by herbaceous annuals (<2m).
        veg_mask[veg_mask == 11] = allrest_id # Permanent Wetlands: permanently inundated lands with 30-60% water cover and >10% vegetated cover.
        veg_mask[veg_mask == 12] = grass_id # Croplands: at least 60% of area is cultivated cropland.
        veg_mask[veg_mask == 13] = allrest_id # Urban and Built-up Lands: at least 30% impervious surface area including building materials, asphalt and vehicles.
        veg_mask[veg_mask == 14] = allrest_id # Cropland/Natural Vegetation Mosaics: mosaics of small-scale cultivation 40-60% with natural tree, shrub, or herbaceous vegetation.
        veg_mask[veg_mask == 15] = allrest_id # Permanent Snow and Ice: at least 60% of area is covered by snow and ice for at least 10 months of the year.
        veg_mask[veg_mask == 16] = allrest_id # Barren: at least 60% of area is non-vegetated barren (sand, rock, soil) areas with less than 10% vegetation.
        veg_mask[veg_mask == 17] = allrest_id # Water Bodies: at least 60% of area is covered by permanent water bodies.
        veg_mask[veg_mask == 254] = allrest_id # fill value
        veg_mask[veg_mask == 255] = allrest_id # fill value
        print(np.unique(veg_mask, return_counts=True))

        src.GetRasterBand(1).WriteArray(veg_mask)
        src.SetGeoTransform(mask_tile.GetGeoTransform())
        src.SetProjection(mask_tile.GetProjection())

        err = gdal.ReprojectImage(src, dst, None, None, gdal.GRA_NearestNeighbour)
        print(err)
  
    
    return dst.ReadAsArray()








if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="""create vegetation mask 1-grass 2-shrub 3-forest""")
    parser.add_argument('-infolder', '--inputfolder', type=str, required=True, help="path to folder with input mcd12q1 data")
    parser.add_argument('-forestid', '--forestid', type=str, required=True, help="value to give to forest pixels, recommended 3")
    parser.add_argument('-shrubid', '--shrubid', type=str, required=True, help="value to give to shrubland pixels, recommended 2")
    parser.add_argument('-grassid', '--grassid', type=str, required=True, help="value to give to grassland and cropland pixels, recommended 1")
    parser.add_argument('-allrestid', '--allrestid', type=str, required=True, help="value to give to all rest of land cover types pixels, recommended 0")
    parser.add_argument('-ystart', '--yearstart', type=str, required=True, help="first year of interest")
    parser.add_argument('-yend', '--yearend', type=str, required=True, help="last year of interest")
    parser.add_argument('-outfolder', '--outputfolder', required=True, type=str, help="path to folder where to save output")
    args = parser.parse_args()


    # example for running script
    # /g/data/xc0/software/conda-envs/rs3/bin/python /g/data/xc0/user/scortechini/github/fire-data-processing/deciles/zonalstats_veg_mask.py -infolder /g/data/ub8/au/FMC/intermediary_files/MCD12Q1.061 -forestid 3 -shrubid 2 -grassid 1 -allrestid 0 -ystart 2001 -yend 2023 -outfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask
    
    au_tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11"]

    forest_id, shrub_id, grass_id, allrest_id = int(args.forestid), int(args.shrubid), int(args.grassid), int(args.allrestid)

    year_start, year_end = int(args.yearstart), int(args.yearend)

    for y in range(year_start, year_end+1):

        veg_mask_array = compose_veg_mask_mosaic(y, args.inputfolder, au_tiles, forest_id, shrub_id, grass_id, allrest_id)
        np.savez_compressed('{}/veg_mask_{}.npz'.format(args.outputfolder, y), veg_mask=veg_mask_array)


