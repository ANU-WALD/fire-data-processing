import os
import argparse
from datetime import datetime

au_tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-y', '--year', help='Year for the modis tiles', type=int, required=True)
    args = parser.parse_args()

    for au_tile in au_tiles:
        print("qsub -v 'year={0},tile={1}' fmc_rec.qsub".format(args.year, au_tile))
        #os.system('qsub -v "year={0},tile={1}" fmc.qsub'.format(args.year, au_tile))
        os.system('qsub -v "year={0},tile={1}" fmc_rec.qsub'.format(args.year, au_tile))
