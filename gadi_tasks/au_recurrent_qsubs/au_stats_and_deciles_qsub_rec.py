
import os
import xarray as xr

if __name__ == "__main__":
    for year in range(2021,2022):
        print(year)
        if os.path.isfile('/g/data/ub8/au/FMC/c6/mosaics/deciles/fmc_c6_{}_dc.nc'.format(year)):
            deciles = xr.open_dataset('/g/data/ub8/au/FMC/c6/mosaics/deciles/fmc_c6_{}_dc.nc'.format(year))
            lfmc = xr.open_dataset('/g/data/ub8/au/FMC/c6/mosaics/fmc_c6_{}.nc'.format(year))
            if deciles.time.data[-1] == lfmc.time.data[-1]:
                os.system('qsub /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_recurrent_qsubs/for_not_running_dec_every_day.qsub')
            else:
                os.system('qsub -v "year={0}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_recurrent_qsubs/au_stats_and_deciles_rec.qsub'.format(year))
        else:
            os.system('qsub -v "year={0}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_recurrent_qsubs/au_stats_and_deciles_rec.qsub'.format(year))

