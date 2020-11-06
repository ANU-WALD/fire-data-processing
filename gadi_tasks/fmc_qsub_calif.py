import os


tiles = ["h08v05", "h08v04", "h09v04"]

if __name__ == "__main__":
    for year in range(2006,2007):
        for tile in tiles:
            print("qsub -v 'year={0},tile={1}' /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_calif.qsub".format(year, tile))
            os.system('qsub -v "year={0},tile={1}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_calif.qsub'.format(year, tile))
