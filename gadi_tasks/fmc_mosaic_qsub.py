import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-y', '--year', help='Year for the modis tiles', type=int, required=True)
    args = parser.parse_args()

    print("qsub -v 'year={0}' fmc_mosaic_rec.qsub".format(args.year))
    os.system('qsub -v "year={0}" fmc_mosaic.qsub'.format(args.year))
    #os.system('qsub -v "year={0}" fmc_mosaic_rec.qsub'.format(args.year))
