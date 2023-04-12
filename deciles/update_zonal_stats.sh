module load cdo

/g/data/xc0/software/conda-envs/rs3/bin/python /g/data/xc0/user/scortechini/github/fire-data-processing/deciles/zonalstats_update_rank_with_deciles.py -decfolder /g/data/ub8/au/FMC/intermediary_files/deciles_arrays -mosfolder /g/data/ub8/au/FMC/mosaics -var both -ystart 2023 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats -tmpfolder /g/data/ub8/au/FMC/tmp


/g/data/xc0/software/conda-envs/rs3/bin/python /g/data/xc0/user/scortechini/github/fire-data-processing/deciles/zonalstats_zonal_stats_absolute.py -mosfolder /g/data/ub8/au/FMC/mosaics -vegmaskfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask -areafolder /g/data/ub8/au/FMC/intermediary_files/areal_classifications -area both -var both -ystart 2023 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats/zonal_stats -tmpfolder /g/data/ub8/au/FMC/tmp


/g/data/xc0/software/conda-envs/rs3/bin/python /g/data/xc0/user/scortechini/github/fire-data-processing/deciles/zonalstats_zonal_stats_relative.py -decfolder /g/data/ub8/au/FMC/stats -vegmaskfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask -areafolder /g/data/ub8/au/FMC/intermediary_files/areal_classifications -area both -var both -ystart 2023 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats/zonal_stats -tmpfolder /g/data/ub8/au/FMC/tmp
