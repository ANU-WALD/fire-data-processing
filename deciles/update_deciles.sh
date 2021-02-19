

/g/data/xc0/software/python/miniconda3/bin/python3 03_calc_single_year_deciles.py flammability /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp 2021
/g/data/xc0/software/python/miniconda3/bin/python3 03_calc_single_year_deciles.py fmc_mean /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp 2021


/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_deciles.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp flammability 2021 LGA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_deciles.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp flammability 2021 FWA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_deciles.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp fmc_mean 2021 LGA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_deciles.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp fmc_mean 2021 FWA


/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_org_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp flammability 2021 LGA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_org_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp flammability 2021 FWA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_org_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp fmc_mean 2021 LGA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_org_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp fmc_mean 2021 FWA

/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp LGA flammability
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp FWA flammability
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp LGA fmc_mean
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp FWA fmc_mean

/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc_org_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp LGA flammability
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc_org_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp FWA flammability
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc_org_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp LGA fmc_mean
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc_org_nc.py /g/data/xc0/project/FMC_Australia/calc_deciles/data/temp FWA fmc_mean
