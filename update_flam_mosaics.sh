module load cdo

/g/data1/xc0/software/conda-envs/rs3/bin/python update_flammability_mosaic.py -y 2019 -dst /g/data/ub8/au/FMC/flam_mosaics_geotransform_corrected/flam_c6_2019.nc -tmp /g/data/xc0/tmp2/
/g/data1/xc0/software/conda-envs/rs3/bin/python update_flammability_mosaic.py -y 2020 -dst /g/data/ub8/au/FMC/flam_mosaics_geotransform_corrected/flam_c6_2020.nc -tmp /g/data/xc0/tmp2/
