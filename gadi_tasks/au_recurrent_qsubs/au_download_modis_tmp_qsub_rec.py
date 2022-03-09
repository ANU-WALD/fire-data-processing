import os

if __name__ == "__main__":
    year = 2021
    print(year)
    os.system('qsub -v "year={0}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_recurrent_qsubs/au_download_modis_tmp_rec.qsub'.format(year))
