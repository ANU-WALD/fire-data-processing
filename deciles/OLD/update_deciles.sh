

/g/data/xc0/software/python/miniconda3/bin/python3 03_calc_single_year_deciles.py flammability /g/data/ub8/au/FMC/calc_deciles/data/temp 2022
/g/data/xc0/software/python/miniconda3/bin/python3 03_calc_single_year_deciles.py fmc_mean /g/data/ub8/au/FMC/calc_deciles/data/temp 2022


/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_deciles.py /g/data/ub8/au/FMC/calc_deciles/data/temp flammability 2022 LGA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_deciles.py /g/data/ub8/au/FMC/calc_deciles/data/temp flammability 2022 FWA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_deciles.py /g/data/ub8/au/FMC/calc_deciles/data/temp fmc_mean 2022 LGA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_deciles.py /g/data/ub8/au/FMC/calc_deciles/data/temp fmc_mean 2022 FWA


/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_org_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp flammability 2022 LGA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_org_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp flammability 2022 FWA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_org_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp fmc_mean 2022 LGA
/g/data/xc0/software/python/miniconda3/bin/python3 04_zonal_statistics_org_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp fmc_mean 2022 FWA

/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp LGA flammability
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp FWA flammability
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp LGA fmc_mean
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp FWA fmc_mean

/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc_org_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp LGA flammability
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc_org_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp FWA flammability
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc_org_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp LGA fmc_mean
/g/data/xc0/software/python/miniconda3/bin/python3 05_zonal_statistics_deciles_merge_to_nc_org_nc.py /g/data/ub8/au/FMC/calc_deciles/data/temp FWA fmc_mean
