import os.path
from osgeo import gdal
import numpy as np
import argparse
from utils import pack_data, get_top_n_functor


def get_fmc_image(rasters, landcover_mask, q_mask):

    # In case the mask doesn't exist
    if q_mask is None:
        q_mask = np.ones(landcover_mask.shape, dtype=bool)

    mean_arr = np.zeros(landcover_mask.shape, dtype=np.float32)
    std_arr = np.zeros(landcover_mask.shape, dtype=np.float32)

    get_mean_std = get_top_n_functor(n=40)

    y_size, x_size = landcover_mask.shape[-2:]

    for i in range(x_size):
        for j in range(y_size):
            if landcover_mask[j, i] > .0 and q_mask[j, i]:
                mean_arr[j, i], std_arr[j, i] = \
                    get_mean_std(rasters[j, i, :], landcover_mask[j, i])

    return mean_arr, std_arr


def aggregator(tile_path, landcover_mask, pq_mask_path):
    #Special case where we don't use all the bands 1, 2, 4, 6, 7
    file_pattern = 'HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:Nadir_Reflectance_Band{}'
    bands = [gdal.Open(file_pattern.format(tile_path, b)) for b in [1, 2, 4, 6, 7]]

    raster_stack = bands[0].GetRasterBand(1).ReadAsArray() * .0001
    for b in range(1, len(bands)):
        raster_stack = np.dstack(
            (raster_stack, bands[b].GetRasterBand(1).ReadAsArray() * .0001))


    red, nir = raster_stack[..., 0], raster_stack[..., 1]
    ndvi_mask = ((nir - red) / (nir + red)) > 0.15

    # NDII compositions between bands 2 and 6 -> indexes 1 and 3
    NDII = (nir - raster_stack[:, :, 3]) / (nir + raster_stack[:, :, 3])
    #raster stack contains 6 bands: 5 bands from the sat rasters and the NDII one
    raster_stack = np.dstack((raster_stack, NDII))

    return get_fmc_image(
        raster_stack,
        auraster=gdal.Open(landcover_mask).GetRasterBand(1).ReadAsArray(),
        q_mask=np.logical_and(quality_mask_composer(pq_mask_path), ndvi_mask)
        )


def quality_mask_composer(pq_mask_path):

    if not os.path.isfile(pq_mask_path):
        return None

    base = 'HDF4_EOS:EOS_GRID:"{}":MOD_Grid_BRDF:'.format(pq_mask_path)
    albedo = gdal.Open(base + 'BRDF_Albedo_Quality')
    albedo_band = gdal.Open(base + 'BRDF_Albedo_Band_Quality')
    snow = gdal.Open(base + 'Snow_BRDF_Albedo')

    albedo_mask = np.equal(albedo.ReadAsArray(), 0)
    albedo_band_mask = np.equal(albedo_band.ReadAsArray(), 0)
    snow_mask = np.equal(snow.ReadAsArray(), 0)

    return np.logical_and(np.logical_and(snow_mask, albedo_mask),
                          albedo_band_mask)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""Modis Vegetation Analysis argument parser""")
    parser.add_argument(
        dest="modis_tile", type=str,
        help="Full path to a modis tile (HDF-EOS).")
    parser.add_argument(
        dest="landcover_mask", type=str,
        help="Full path to the vegetation mask (GeoTIFF).")
    parser.add_argument(
        dest="pq_mask", type=str,
        help="Full path to the pixel quality product mask (HDF-EOS).")
    parser.add_argument(
        dest="destination", type=str,
        help="Full path to destination.")
    args = parser.parse_args()

    mean, stdv = aggregator(args.modis_tile, args.landcover_mask, args.pq_mask)

    pack_data(args.modis_tile, mean, stdv, args.destination)

