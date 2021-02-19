
import os
import xarray as xr

if __name__ == "__main__":
    for year in range(2021,2022):
        print(year)
        os.system('qsub -v "year={0}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_one_time_qsubs/au_deciles_test.qsub'.format(year))

