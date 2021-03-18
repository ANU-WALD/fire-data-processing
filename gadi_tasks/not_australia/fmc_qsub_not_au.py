import os


tiles = ["h20v05", "h20v06"]

if __name__ == "__main__":
    for year in range(2018,2019):
        for tile in tiles:
            print("qsub -v 'year={0},tile={1}' /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/not_australia/fmc_not_au.qsub".format(year, tile))
            os.system('qsub -v "year={0},tile={1}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/not_australia/fmc_not_au.qsub'.format(year, tile))
