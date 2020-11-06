import os

tiles = ['h19v11','h19v12','h20v11','h20v12']

if __name__ == "__main__":
    #for year in range(2001,2021):
        #for tile in tiles:
            #print("qsub -v 'year={0},tile={1}' /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_safrica.qsub".format(year, tile))
            #os.system('qsub -v "year={0},tile={1}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_safrica.qsub'.format(year, tile))

    year=2012
    for tile in ['h19v12','h20v11']:
        print("qsub -v 'year={0},tile={1}' /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_safrica.qsub".format(year, tile))
        os.system('qsub -v "year={0},tile={1}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_safrica.qsub'.format(year, tile))

    year=2019
    for tile in ['h19v11']:
        print("qsub -v 'year={0},tile={1}' /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_safrica.qsub".format(year, tile))
        os.system('qsub -v "year={0},tile={1}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_safrica.qsub'.format(year, tile))

    year=2018
    for tile in ['h20v12','h20v11']:
        print("qsub -v 'year={0},tile={1}' /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_safrica.qsub".format(year, tile))
        os.system('qsub -v "year={0},tile={1}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_safrica.qsub'.format(year, tile))
