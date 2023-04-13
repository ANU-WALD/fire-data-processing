## Fire Data Processing -- ANU-WALD

The Fire Data Processing repository is a collection of scripts used to produce the fuel moisture and flammability data for usage on the online interactive [Australian Flammability Monitoring system (AFMS)](http://wenfo.org/afms/).

This is a research initiative to provide quality spatial information on fire hazards in Australia to better understand the risk of bushfires, their severity and preparing ways to respond to them.


### Important Links
---
* [The Project](http://www.bnhcrc.com.au/research/understanding-mitigating-hazards/255)
* [Australian Flammability Monitoring System](http://wenfo.org/afms/)


### Scripts
---

#### General Usage
\[Last update: April 2023\]

All scripts accept a help argument which displays all input flags. Use "python script.py --help" on the respective script to display help.

You must be in the following NCI project groups to perform certain tasks with these scripts;

* **ub8** - Data Access (**ub8_admin** for write permissions)
* **xc0** - To activate a Python environment with all the required packages
* A project with Gadi allocation, to edit and run the various \*.qsub files


#### Dependencies
\[Last update: December 2019\]

These scripts rely on a range of scientific packages not included in the Python standard library.
If you are a member of the xc0 group on NCI, simply run "source activate rs3" to activate an environment with all the requirements.
(If this does not work, see /g/data/xc0/software/README.xc0-miniconda)

To create your own environment, run the command:

    conda create --name rs3 --channel conda-forge python=3 xarray>=0.10 pynio jupyter

If that doesn't work (eg due to package updates), install from `environment.yml` to get *exactly* the same packages.


#### Repository and Pipeline Explained
\[Last update: April 2023\]

*Please note that the land cover product MCD12Q1 (used by several scripts to generate the output data) is updated yearly. Thus, there might be a lag of 1 year or more between the most recent dates of MCD43A4 (the reflectance data which the Live Fuel Moisture Content outputs rely on) and the last year of available land cover data. For those dates within the lag period, the most recent year available in MCD12Q1 is used.*
*It is recommended to update the LFMC, flammability and any other output data that depend on MCD12Q1, when new MCD12Q1 data is avaiable. This could mean re-creating netCDF files containing year-long time-series.*


The core scripts and files are in the folder **"main\_lfmc\_flam"**:
* "FMC.npy" and "LUT.npy" compose the lookup table used to match reflectance data to Live Fuel Moisture Content (LFMC) values.
* "nc_metadata.json" contains the metadata copied into the LFMC and flammability netCDF files.
* "update\_fmc.py" is used to create or update (if already existing) the LFMC tiles starting from MCD43A4 reflectance data and MCD12Q1 IGBP land cover data. This script should be run whenever new MCD43A4 data is available. The following is an example command that can be used to run the script:
```
    module load cdo
    /g/data/xc0/software/conda-envs/rs3/bin/python update_fmc.py -d 2023 -t h27v11 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h27v11.nc -tmp /g/data/ub8/au/FMC/tmp/
```
* "update\_fmc\_mosaic.py" creates or updates (if already existing) the LFMC mosaics. This script should be run after the LFMC tiles are updated. The following is an example command that can be used to run the script:
```
    module load cdo
    /g/data/xc0/software/conda-envs/rs3/bin/python update_fmc_mosaic.py -y 2023 -dst /g/data/ub8/au/FMC/mosaics/fmc_c6_2023.nc -tmp /g/data/ub8/au/FMC/tmp/
```
* "cdo_mean.py" is used to generate mean LFMC values tiles used to retrieve flammability data. This script can be run when it is decided to update the reference time series.
* "update\_flammability.py" is used to generate or update (if already existing) the flammability tiles using the LFMC tiles and mean LFMC values tiles as starting point. This script should be run after the LFMC tiles are updated. The following is an example command that can be used to run the script:
```
    module load cdo
    /g/data/xc0/software/conda-envs/rs3/bin/python update_flammability.py -y 2023 -t h32v11 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h32v11.nc -tmp /g/data/ub8/au/FMC/tmp/
```
* "update\_flammability\_mosaic.py" creates or updates (if already existing) the flammability mosaics. This script should be run after the flammability tiles are updated. The following is an example command that can be used to run the script:
```
    module load cdo
    /g/data/xc0/software/conda-envs/rs3/bin/python update_flammability_mosaic.py -y 2023 -dst /g/data/ub8/au/FMC/mosaics/flam_c6_2023.nc -tmp /g/data/ub8/au/FMC/tmp/
```
* "utils.py" contains functions employed in the other scripts. It does not need to be run.
* "update\_fmc\_flam.sh" is a shell script that can be used to update all the LFMC and flammability tiles and their mosaics. This script can be run after new MCD43A4 data becomes available. The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/main_lfmc_flam/
    chmod +x ./update_fmc_flam.sh
    ./update_fmc_flam.sh
```
* "ALTERNATIVE\_update\_fmc\_different\_mcd43a4\_path.py" and "ALTERNATIVE\_update\_fmc\_every8days.py" are variants of the main scripts that can be used if the directory to MODIS tiles is different or if needed to create 8-daily LFMC tiles.


The folder **"deciles"** contains scripts to create and update statistics on LFMC and flammability data:
* "zonalstats\_veg\_mask.py" generates the vegetation type masks using MCD12Q1 IGBP land cover data. 3 == forest, 2 == shrub, 1 == grass/cropland, 0 == all the rest. Details on what categories are included in each classification can be found in the script itself. This script can be run when new yearly MCD12Q1 is available. The following is an example command that can be used to run the script: 
```
    /g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_veg_mask.py -infolder /g/data/ub8/au/FMC/intermediary_files/MCD12Q1.061 -forestid 3 -shrubid 2 -grassid 1 -allrestid 0 -ystart 2001 -yend 2023 -outfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask

```
* "zonalstats\_stack\_by\_month.py" creates 3D arrays by merging together all LFMC (or flammability) daily arrays belonging to the same month (e.g., "fmc\_month1.npz" contains all LFMC mosaics dated from 1st to 31st Januray 2001, 1st to 31st Januray 2002, [...], 1st to 31st Januray 2022). This script can be run only once at the start, or when it is needed to update the reference time series (using Gadi is recommended). The following is an example command that can be used to run the script:
```
    /g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_stack_by_month.py -infolder /g/data/ub8/au/FMC/mosaics -var both -ystart 2001 -yend 2022 -outfolder /g/data/ub8/au/FMC/intermediary_files/stack_by_month_2001_2022
```
* "zonalstats\_calculate\_deciles.py" calculates the 10th, 20th, 30th, [...], 90th percentile arrays for every month using the 3D month arrays created with "zonalstats\_stack\_by\_month.py". The output arrays are 2D arrays where every pixel's value is the Xth percentile along the time dimension (e.g., "fmc\_month1\_percentile10.npz" is a 2D array where every pixel's value is the 10th percentile (or 1st decile) of the LFMC values on that pixel across all January dates from 2001 to 2022). This script can be run only once after "zonalstats\_stack\_by\_month.py" (using Gadi is recommended). The following is an example command that can be used to run the script:
```
    /g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_calculate_deciles.py -infolder /g/data/ub8/au/FMC/intermediary_files/stack_by_month_2001_2022 -var both -month all -outfolder /g/data/ub8/au/FMC/intermediary_files/deciles_arrays
```
* "zonalstats\_rank\_with\_deciles.py" creates netCDF files grouped by year and variable (either LFMC or flammability) which contain the decile ranking of every LFMC or flammability mosaic across the whole time series. The information is extracted by comparing each daily mosaic with the percentiles arrays created with "zonalstats\_calculate\_deciles.py". This script should be run when the reference time series has been changed, after running "zonalstats\_stack\_by\_month.py" and "zonalstats\_calculate\_deciles.py" (using Gadi is recommended). The following is an example command that can be used to run the script:
```
    /g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_rank_with_deciles.py -decfolder /g/data/ub8/au/FMC/intermediary_files/deciles_arrays -mosfolder /g/data/ub8/au/FMC/mosaics -var both -ystart 2001 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats
```
* "zonalstats\_update\_rank\_with\_deciles.py": same as "zonalstats\_rank\_with\_deciles.py", but it can be run to modify already existing netCDF files and add only the dates missing to be up to date with the LFMC and flammability mosaics. This script can be run whenever LFMC and flammability mosaics are updated. The following is an example command that can be used to run the script:
```
    module load cdo
    /g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_update_rank_with_deciles.py -decfolder /g/data/ub8/au/FMC/intermediary_files/deciles_arrays -mosfolder /g/data/ub8/au/FMC/mosaics -var both -ystart 2023 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats -tmpfolder /g/data/ub8/au/FMC/tmp
```
* "zonalstats\_zonal\_stats\_absolute.py" creates or updates netCDF files containing LFMC and flammability zonal statistics, using the LFMC and flammability mosaics as starting point. The areas on which this statistics are computed are either Local Government Areas or Fire Weather Areas. For each area the following information on LFMC or flammability is reported: the areal average, maximum and minimum of the full area, of the forest pixels within the area, of shurb pixels and of the grass/crop pixels. Moreover, it also present a variable reporting the spatial coverage of each land cover type within the areas (i.e., land cover type pixels / total area pixels * 100). This script can be run whenever LFMC and flammability mosaics are updated. The following is an example command that can be used to run the script:
```
    module load cdo
    /g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_zonal_stats_absolute.py -mosfolder /g/data/ub8/au/FMC/mosaics -vegmaskfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask -areafolder /g/data/ub8/au/FMC/intermediary_files/areal_classifications -area both -var both -ystart 2001 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats/zonal_stats/new -tmpfolder /g/data/ub8/au/FMC/tmp 

```
* "zonalstats\_zonal\_stats\_relative.py" creates or updates netCDF files containing zonal statistics similarly to "zonalstats\_zonal\_stats\_absolute.py". However, these statistics are calculated from the decile ranking files generated with "zonalstats\_rank\_with\_deciles.py" or "zonalstats\_update\_rank\_with\_deciles.py". This script can be run whenever the decile ranking files are updated. The following is an example command that can be used to run the script:
```
    module load cdo
    /g/data/xc0/software/conda-envs/rs3/bin/python zonalstats_zonal_stats_relative.py -decfolder /g/data/ub8/au/FMC/stats -vegmaskfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask -areafolder /g/data/ub8/au/FMC/intermediary_files/areal_classifications -area both -var both -ystart 2001 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats/zonal_stats/new -tmpfolder /g/data/ub8/au/FMC/tmp

```
* "update\_zonal\_stats.sh" is a shell script that can be used to update both the absolute and relative zonal statistics. This script can be run when the LFMC and flammability mosaics are updated. The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/deciles/
    chmod +x ./update_zonal_stats.sh
    ./update_zonal_stats.sh
```

**gadi\_tasks**

**others**

**workspace**

**update\_all.sh**

### Access and Description of the Output Data
---

