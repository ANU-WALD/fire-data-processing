
module load cdo
cd /g/data/xc0/user/scortechini/github/fire-data-processing

/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability_NEW.py -y 2020 -t h32v11 -dst /g/data/ub8/au/FMC/test_new_flam/flam_c6_2020_h32v11.nc -tmp /g/data/xc0/tmp/


