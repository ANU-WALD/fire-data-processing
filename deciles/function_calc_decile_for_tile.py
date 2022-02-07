import sys
from functions_io import load_pickle, save_pickle
import os
import numpy as np
from copy import copy

tile_path_file = sys.argv[1]
# tile_path_file = '/g/data/ub8/au/FMC/calc_deciles/data/temp/temp_tiles/flam_1.nc/flammability__1.pk'
tile_path = os.path.dirname(tile_path_file)
tile_file = os.path.basename(tile_path_file)

tile_dc_path = tile_path + '/' + 'deciles'
if not os.path.exists(tile_dc_path):
    os.mkdir(tile_dc_path)

tile_dc_file = tile_file.replace('.pk', '_dc.pk')
tile_dc_path_file = tile_dc_path + '/' + tile_dc_file

print('started *****,', tile_file)

tile_dict = load_pickle(tile_path_file)

dc_dict = copy(tile_dict)
del dc_dict['data']
dc_dict['deciles'] = {}


cnt_q = 0
for q in range(10, 100, 10):
    dc_dict['deciles'][q] = np.nanpercentile(tile_dict['data'], q, axis=0)
    cnt_q += 1

save_pickle(dc_dict, tile_dc_path_file)

print('saved ******', tile_file)

