module load cdo






/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc_nsw.py -d 2021 -t h29v12 -dst /g/data/ub8/au/FMC/NSW/tiles/NSW_fmc_c6_2021_h29v12.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc_nsw.py -d 2021 -t h30v11 -dst /g/data/ub8/au/FMC/NSW/tiles/NSW_fmc_c6_2021_h30v11.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc_nsw.py -d 2021 -t h30v12 -dst /g/data/ub8/au/FMC/NSW/tiles/NSW_fmc_c6_2021_h30v12.nc -tmp /g/data/ub8/au/FMC/tmp/

/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc_mosaic_nsw.py -y 2021 -dst /g/data/ub8/au/FMC/NSW/mosaics/NSW_fmc_c6_2021.nc -tmp /g/data/ub8/au/FMC/tmp/

