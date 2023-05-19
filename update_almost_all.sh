module load cdo

cd /g/data/xc0/user/scortechini/github/fire-data-processing/main_lfmc_flam

/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h27v11 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h27v11.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h27v12 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h27v12.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h28v11 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h28v11.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h28v12 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h28v12.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h28v13 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h28v13.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h29v10 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h29v10.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h29v11 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h29v11.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h29v12 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h29v12.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h29v13 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h29v13.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h30v10 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h30v10.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h30v11 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h30v11.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h30v12 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h30v12.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h31v10 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h31v10.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h31v11 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h31v11.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h31v12 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h31v12.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h32v10 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h32v10.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h32v11 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h32v11.nc -tmp /g/data/ub8/au/FMC/tmp/

/g/data/xc0/software/conda-envs/rs3/bin/python update_fmc_mosaic.py -y 2023 -dst /g/data/ub8/au/FMC/mosaics/fmc_c6_2023.nc -tmp /g/data/ub8/au/FMC/tmp/

/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h27v11 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h27v11.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h27v12 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h27v12.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h28v11 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h28v11.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h28v12 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h28v12.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h28v13 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h28v13.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h29v10 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h29v10.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h29v11 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h29v11.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h29v12 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h29v12.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h29v13 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h29v13.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h30v10 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h30v10.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h30v11 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h30v11.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h30v12 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h30v12.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h31v10 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h31v10.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h31v11 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h31v11.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h31v12 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h31v12.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h32v10 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h32v10.nc -tmp /g/data/ub8/au/FMC/tmp/
/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h32v11 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h32v11.nc -tmp /g/data/ub8/au/FMC/tmp/

/g/data/xc0/software/conda-envs/rs3/bin/python update_flammability_mosaic.py -y 2023 -dst /g/data/ub8/au/FMC/mosaics/flam_c6_2023.nc -tmp /g/data/ub8/au/FMC/tmp/


cd /g/data/xc0/user/scortechini/github/fire-data-processing/deciles

/g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_update_rank_with_deciles.py -decfolder /g/data/ub8/au/FMC/intermediary_files/deciles_arrays -mosfolder /g/data/ub8/au/FMC/mosaics -var both -ystart 2023 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats -tmpfolder /g/data/ub8/au/FMC/tmp

/g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_zonal_stats_absolute.py -mosfolder /g/data/ub8/au/FMC/mosaics -vegmaskfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask -areafolder /g/data/ub8/au/FMC/intermediary_files/areal_classifications -area fwa -var both -ystart 2023 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats/zonal_stats -tmpfolder /g/data/ub8/au/FMC/tmp 

/g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_zonal_stats_relative.py -decfolder /g/data/ub8/au/FMC/stats -vegmaskfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask -areafolder /g/data/ub8/au/FMC/intermediary_files/areal_classifications -area fwa -var both -ystart 2023 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats/zonal_stats -tmpfolder /g/data/ub8/au/FMC/tmp
