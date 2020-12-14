import os

if __name__ == "__main__":
    for year in range(2001,2021):
        print(year)
        os.system('qsub -v "year={0}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_flamm_mosaics.qsub'.format(year))
