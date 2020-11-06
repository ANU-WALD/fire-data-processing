import os
import argparse
from datetime import datetime

au_tiles = ["h08v05"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-y', '--year', help='Year for the modis tiles', type=int, required=True)
    args = parser.parse_args()


    for au_tile in au_tiles:
        print("qsub -v 'year={0},tile={1}' flam.qsub".format(args.year, au_tile))
        os.system('qsub -v "year={0},tile={1}" flam.qsub'.format(args.year, au_tile))
