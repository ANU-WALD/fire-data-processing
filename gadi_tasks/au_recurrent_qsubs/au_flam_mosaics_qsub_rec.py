import os

if __name__ == "__main__":
    for year in range(2021,2022):
        print(year)
        os.system('qsub -v "year={0}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_recurrent_qsubs/au_flam_mosaics_rec.qsub'.format(year))
