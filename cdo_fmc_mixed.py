import os
import argparse
from datetime import datetime

tiles_dates = {
	       'h21v10':[20190621, 20190623, 20190624, 20190625, 20190626, 20190627, 20190701, 20190702, 20190707, 20191007, 20191008, 20191009, 20191010, 20191011, 20191012, 20191013, 20191014, 20191016, 20191017, 20191018],

               'h13v10':[20170911, 20170913, 20170914, 20170915, 20170916, 20170919, 
                         20180617, 20180618, 20180619, 20180620, 20180621, 20180622, 20180623, 20180625, 20180626, 20180628, 20180629, 20180923, 20180924, 20180927, 20181003, 20181004, 20181010],

	       'h20v11':[20180821, 20180828, 20180829, 20180830],

	       'h20v10':[20190524,20190525,20190605,20190606,20190906,20190907,20190909,20190910,20190911,20190913],

               'h19v10':[20190601]
               
		}


if __name__ == "__main__":
    for i in tiles_dates.items():
        tile = i[0]
        for date in i[1]:
            print(tile, date)
            os.system('module load cdo')
            os.chdir('/g/data/xc0/user/scortechini/github/fire-data-processing')
            os.system('/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc_different_mcd43a4_path.py -d {0} -t {1} -dst  /g/data/xc0/user/scortechini/mixed_tiles/fmc_c6_{1}.nc -tmp /g/data/xc0/tmp/'.format(date, tile))
