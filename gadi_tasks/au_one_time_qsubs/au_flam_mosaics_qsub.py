import os

if __name__ == "__main__":
    for year in reversed(range(2001,2021)):
        print(year)
        os.system('qsub -v "year={0}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_one_time_qsubs/au_flam_mosaics.qsub'.format(year))
