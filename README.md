## Fire Data Processing -- ANU-WALD

The Fire Data Processing repository is a collection of scripts used to produce the fuel moisture and flammability data for usage on the online interactive [Australian Flammability Monitoring system (AFMS)](http://wenfo.org/afms/).

This is a research initiative to provide quality spatial information on fire hazards in Australia to better understand the risk of bushfires, their severity and preparing ways to respond to them.


### Important Links
---
* [The Project](http://www.bnhcrc.com.au/research/understanding-mitigating-hazards/255)
* [Australian Flammability Monitoring System](http://wenfo.org/afms/)
* [Reference (Yebra et al. 2018)](https://doi.org/10.1016/j.rse.2018.04.053)


### Scripts
---

#### General Usage
\[Last update: April 2023\]

All scripts accept a help argument which displays all input flags. Use "python script.py --help" on the respective script to display help.

You must be in the following NCI project groups to perform certain tasks with these scripts;

* **ub8** - Data Access (**ub8_admin** for write permissions)
* **xc0** - To activate a Python environment with all the required packages
* A project with Gadi allocation, to edit and run the various .qsub files


#### Dependencies
\[Last update: December 2019\]

These scripts rely on a range of scientific packages not included in the Python standard library.
If you are a member of the xc0 group on NCI, simply run "source activate rs3" to activate an environment with all the requirements.
(If this does not work, see /g/data/xc0/software/README.xc0-miniconda)

To create your own environment, run the command:

    conda create --name rs3 --channel conda-forge python=3 xarray>=0.10 pynio jupyter

If that doesn't work (eg due to package updates), install from `environment.yml` to get *exactly* the same packages.


#### Repository and Pipeline Explained
\[Last update: Sep 2023\]

*Please note that the land cover product MCD12Q1 (used by several scripts to generate the output data) is updated yearly. Thus, there might be a lag of 1 year or more between the most recent dates of MCD43A4 (the reflectance data which the Live Fuel Moisture Content outputs rely on) and the last year of available land cover data. For those dates within the lag period, the most recent year available in MCD12Q1 is used.*
*It is recommended to update the LFMC, flammability and any other output data that depend on MCD12Q1, when new MCD12Q1 data is avaiable. This could mean re-creating netCDF files containing year-long time series.*


The core scripts and files are in the folder **"main\_lfmc\_flam"**:
* "<ins>FMC.npy</ins>" and "<ins>LUT.npy</ins>" compose the lookup table used to match reflectance data to Live Fuel Moisture Content (LFMC) values.
* "<ins>nc_metadata.json</ins>" contains the metadata copied into the LFMC and flammability netCDF files.
* "<ins>update\_fmc.py</ins>" is used to create or update (if already existing) the LFMC tiles starting from MCD43A4 reflectance data and MCD12Q1 IGBP land cover data. This script should be run whenever new MCD43A4 data is available. The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/main_lfmc_flam/
    module load cdo
    /ENVIRONMENT_PATH/bin/python update_fmc.py -d 2023 -t h27v11 -dst /g/data/ub8/au/FMC/tiles/fmc_c6_2023_h27v11.nc -tmp /g/data/ub8/au/FMC/tmp/
```
* "<ins>update\_fmc\_mosaic.py</ins>" creates or updates (if already existing) the LFMC mosaics. This script should be run after the LFMC tiles are updated. The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/main_lfmc_flam/
    module load cdo
    /ENVIRONMENT_PATH/bin/python update_fmc_mosaic.py -y 2023 -dst /g/data/ub8/au/FMC/mosaics/fmc_c6_2023.nc -tmp /g/data/ub8/au/FMC/tmp/
```
* "<ins>lfmc\_doy\_means.py</ins>" is used to generate mean LFMC tiles used to retrieve flammability data. This script can be run when it is decided to update the time series of reference.
* "<ins>update\_flammability.py</ins>" is used to generate or update (if already existing) the flammability tiles using the LFMC tiles and mean LFMC tiles as starting point. This script can be run after the LFMC tiles are updated. The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/main_lfmc_flam/
    module load cdo
    /ENVIRONMENT_PATH/bin/python update_flammability.py -y 2023 -t h32v11 -dst /g/data/ub8/au/FMC/tiles/flam_c6_2023_h32v11.nc -tmp /g/data/ub8/au/FMC/tmp/
```
* "<ins>update\_flammability\_mosaic.py</ins>" creates or updates (if already existing) the flammability mosaics. This script should be run after the flammability tiles are updated. The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/main_lfmc_flam/
    module load cdo
    /ENVIRONMENT_PATH/bin/python update_flammability_mosaic.py -y 2023 -dst /g/data/ub8/au/FMC/mosaics/flam_c6_2023.nc -tmp /g/data/ub8/au/FMC/tmp/
```
* "<ins>utils.py</ins>" contains functions employed in the other scripts. It does not need to be run.
* "<ins>update\_fmc\_flam.sh</ins>" is a shell script that can be used to update all the LFMC and flammability tiles and their mosaics. This script can be run after new MCD43A4 data becomes available. The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/main_lfmc_flam/
    chmod +x ./update_fmc_flam.sh
    ./update_fmc_flam.sh
```
* "<ins>ALTERNATIVE\_update\_fmc\_different\_mcd43a4\_path.py</ins>" and "<ins>ALTERNATIVE\_update\_fmc\_every8days.py</ins>" are variants of the main scripts that can be used if the directory to MODIS tiles is different or if needed to create 8-daily LFMC tiles.


The folder **"deciles"** contains scripts to create and update statistics on LFMC and flammability data:
* "<ins>zonalstats\_veg\_mask.py</ins>" generates the vegetation type masks using MCD12Q1 IGBP land cover data. 3 == forest, 2 == shrub, 1 == grass/cropland, 0 == all the rest. Details on what categories are included in each classification can be found in the script itself. This script can be run when new yearly MCD12Q1 is available. The following is an example command that can be used to run the script: 
```
    cd ./fire-data-processing/deciles/
    /ENVIRONMENT_PATH/bin/python zonalstats_veg_mask.py -infolder /g/data/ub8/au/FMC/intermediary_files/MCD12Q1.061 -forestid 3 -shrubid 2 -grassid 1 -allrestid 0 -ystart 2001 -yend 2023 -outfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask
```
* "<ins>zonalstats\_stack\_by\_month.py</ins>" creates 3D arrays by merging together all LFMC (or flammability) daily arrays belonging to the same month (e.g., "fmc\_month1.npz" contains all LFMC mosaics dated from 1st to 31st Januray 2001, 1st to 31st Januray 2002, [...], 1st to 31st Januray 2022). This script can be run only once at the start, or when it is needed to update the reference time series (using Gadi is recommended). The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/deciles/
    /ENVIRONMENT_PATH/bin/python zonalstats_stack_by_month.py -infolder /g/data/ub8/au/FMC/mosaics -var both -ystart 2001 -yend 2022 -outfolder /g/data/ub8/au/FMC/intermediary_files/stack_by_month_2001_2022
```
* "<ins>zonalstats\_calculate\_deciles.py</ins>" calculates the 10th, 20th, 30th, [...], 90th percentile arrays for every month using the 3D month arrays created with "zonalstats\_stack\_by\_month.py". The output arrays are 2D arrays where every pixel's value corresponds to the Xth percentile along the time dimension (e.g., "fmc\_month1\_percentile10.npz" is a 2D array where every pixel's value is the 10th percentile (or 1st decile) of the LFMC values of that pixel across all January dates from 2001 to 2022). This script can be run only once after "zonalstats\_stack\_by\_month.py" (using Gadi is recommended). The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/deciles/
    /ENVIRONMENT_PATH/bin/python zonalstats_calculate_deciles.py -infolder /g/data/ub8/au/FMC/intermediary_files/stack_by_month_2001_2022 -var both -month all -outfolder /g/data/ub8/au/FMC/intermediary_files/deciles_arrays
```
* "<ins>zonalstats\_rank\_with\_deciles.py</ins>" creates yearly netCDF files containing the decile ranking of every LFMC or flammability mosaic across the whole time series. The information is extracted by comparing each daily LFMC or flammability mosaic with the percentiles arrays created with "zonalstats\_calculate\_deciles.py". This script should be run when the reference time series has been changed, after running "zonalstats\_stack\_by\_month.py" and "zonalstats\_calculate\_deciles.py" (using Gadi is recommended). The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/deciles/
    /ENVIRONMENT_PATH/bin/python zonalstats_rank_with_deciles.py -decfolder /g/data/ub8/au/FMC/intermediary_files/deciles_arrays -mosfolder /g/data/ub8/au/FMC/mosaics -var both -ystart 2001 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats
```
* "<ins>zonalstats\_update\_rank\_with\_deciles.py</ins>": same as "zonalstats\_rank\_with\_deciles.py", but it can be run to update already existing netCDF files by adding the most recent dates. This script can be run whenever LFMC and flammability mosaics are updated. The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/deciles/
    module load cdo
    /ENVIRONMENT_PATH/bin/python zonalstats_update_rank_with_deciles.py -decfolder /g/data/ub8/au/FMC/intermediary_files/deciles_arrays -mosfolder /g/data/ub8/au/FMC/mosaics -var both -ystart 2023 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats -tmpfolder /g/data/ub8/au/FMC/tmp
```
* "<ins>zonalstats\_zonal\_stats\_absolute.py</ins>" creates or updates netCDF files containing LFMC and flammability zonal statistics, using the LFMC and flammability mosaics as starting point. The areas on which this statistics are computed are either Local Government Areas or Fire Weather Areas. The statistics reported are the mean, maximum and minimum values of the whole area and of three sub-areas: the forest pixels within the area, the shurb pixels and the grass/crop pixels. Moreover, it also present a variable reporting the spatial coverage of each land cover type within the areas (e.g., forest pixels / total area pixels * 100). This script can be run whenever LFMC and flammability mosaics are updated. The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/deciles/
    module load cdo
    /ENVIRONMENT_PATH/bin/python zonalstats_zonal_stats_absolute.py -mosfolder /g/data/ub8/au/FMC/mosaics -vegmaskfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask -areafolder /g/data/ub8/au/FMC/intermediary_files/areal_classifications -area both -var both -ystart 2001 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats/zonal_stats/new -tmpfolder /g/data/ub8/au/FMC/tmp 

```
* "<ins>zonalstats\_zonal\_stats\_relative.py</ins>" creates or updates netCDF files containing zonal statistics similarly to "zonalstats\_zonal\_stats\_absolute.py". However, these statistics are calculated from the decile ranking files generated with "zonalstats\_rank\_with\_deciles.py" or "zonalstats\_update\_rank\_with\_deciles.py". This script can be run whenever the decile ranking files are updated. The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/deciles/
    module load cdo
    /ENVIRONMENT_PATH/bin/python zonalstats_zonal_stats_relative.py -decfolder /g/data/ub8/au/FMC/stats -vegmaskfolder /g/data/ub8/au/FMC/intermediary_files/vegetation_mask -areafolder /g/data/ub8/au/FMC/intermediary_files/areal_classifications -area both -var both -ystart 2001 -yend 2023 -outfolder /g/data/ub8/au/FMC/stats/zonal_stats/new -tmpfolder /g/data/ub8/au/FMC/tmp

```
* "<ins>update\_zonal\_stats.sh</ins>" is a shell script that can be used to update both the absolute and relative zonal statistics. This script can be run when the LFMC and flammability mosaics are updated. The following is an example command that can be used to run the script:
```
    cd ./fire-data-processing/deciles/
    chmod +x ./update_zonal_stats.sh
    ./update_zonal_stats.sh
```

The scripts in the folder **"gadi\_tasks"** can be used to run the above-mentioned scripts with Gadi. 
Two sub-folders are present: **au\_recurrent\_qsubs** and **au\_one\_time\_qsubs**. The first contains job requests that can re-submit themselves automatically, the second with single use job requests.
Effectively, each request to Gadi is composed by two files: a .qsub file that submits the job to Gadi, and a .py file that creates multiple job requests by looping a .qsub file over different years or tiles. The only file that needs to be run by the user is the python script, which will launch the .qsub file. These two files have almost identical names for facilitating the pairing of the two (e.g. "au\_fmc\_tiles\_qsub.py" and "au\_fmc\_tiles.qsub").
The following is an example command that can be used to run a script with Gadi:
```
    cd ./fire-data-processing/gadi_tasks/au_one_time_qsubs/
    /ENVIRONMENT_PATH/bin/python au_flam_tiles_qsub.py
```

The folder **"others"** contains alternative (and often temporary) python and shell scripts that can be used to create LFMC data for selected regions within Australia or even for other parts of the world.

The folder **"workspace"** contains scripts that are not yet operational.

Finally, **"update\_all.sh"** is a shell script that can be used to update all LFMC and flammability files (tiles, mosaics and statistics files).

### Access and Description of the Output Data
---

The main outputs are georeferenced files (NetCDF) that store Live Fuel Moisture Content (LFMC) and Flammability Index (FI) data.

These files can be in the form of sinusoidal tiles covering a portion of Australia, or WGS84 mosaics showing the whole Australia.

The AFMS data is stored in the NCI and it can be access from the [official web app](http://wenfo.org/afms/), the [online THREDDS catalogue](https://dap.nci.org.au/thredds/remoteCatalogService?catalog=https://dapds00.nci.org.au/thredds/catalog/ub8/au/FMC/catalog.xml) or the NCI's VDI.

#### Accessing the data from the web app
\[Last update: May 2023\]

The website can be accessed from the following link: [http://wenfo.org/afms](http://wenfo.org/afms).

The bar at the top contains 4 to 5 menus that let the user choose:
* whether to show the Live Fuel Moisture Content or the Flammability, 
* the date of interest, 
* what kind of partition to use (e.g. Fire Weather Areas, Local Government Areas),
* if visualise raster data ("Grid"), the areal average or the areal relative values,
* if show the statistics for the entire areas or only for the selected land cover type (this menu appears only if "Areal Average" or "Areal Relative" are selected).

Clicking on any pixel of the map will generate a chart at the bottom of the webpage. The chart shows the LFMC or FI dynamics and statistics corresponding to the coordinates selected: the highest, the lowest and the median values for each day of the year since 2001, and the current year time series. The chart can be downloaded by clicking the dedicated button below it.

From the menu on the left, it is possible to:
* hide all the windows in the webpage,
* adjust the zoom of the map,
* locate a point by coordinates or address,
* modify the transparency of the grid layer,
* choose a different base layer,
* show current incidents,
* download the image for the date selected as a GeoTIFF raster file.

#### Accessing the data from THREDDS
\[Last update: Jul 2023\]

The [THREDDS catalogue](https://dap.nci.org.au/thredds/remoteCatalogService?catalog=https://dapds00.nci.org.au/thredds/catalog/ub8/au/FMC/catalog.xml) is linked to the repository inside the NCI, where all the AFMS files are stored.

There are 5 main folders: "tiles", "mosaics", "stats", "intermediary_files", "tmp". 

* **"tiles"** stores yearly NetCDF files with LFMC and Flammability data in the form of sinusoidal tiles. The spatial resolution of the data is approximately 500m, while the temporal resolution is every 4 days. The names of the files include the type of data they contain (*"fmc"* or *"flam"*), the year and the tile ID (same as the original MODIS tiles). The tiles present in this folder are "h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11".

* **"mosaics"** stores yearly NetCDF files with LFMC and Flammability data in the form of lat/lon (WGS84) mosaics, which cover the whole Australia. The spatial resolution of the data is 500m, while the temporal resolution is every 4 days. The names of these files include the type of data they contain and the year.

* **"stats"** contains yearly mosaicked NetCDF files with the LFMC deciles values. The deciles are computed by taking into account all the dates available from the LFMC mosaics in the period 2001-2022 (inclusive). The subfolder **"zonal_stats"** contains NetCDF files with zonal statistics (e.g. minimum, maximum, mean values) per Fire Weather Area (FWA) or Local Government Area (LGA) (these files are used by the web app for the "Areal Relative" and "Areal Average" features).

* **"intermediary_files"** contains files that are instrumental in the creation of the output data.

* **"tmp"** is a folder used to temporarily store ancillary files created while generating the output data.


#### Accessing the data from the NCI's VDI
\[Last update: May 2023\]

For accessing the data from the NCI's VDI, it is necessary to be an NCI user and request to access to the ub8 project ([as per these instructions](https://opus.nci.org.au/display/Help/How+to+connect+to+a+project)).
The path to the parent directory is: /g/data/ub8/au/FMC.  The repository has the same structure of the THREDDS catalogue.


#### Description of the variables in the AFMS NetCDF files
\[Last update: Jul 2023\]

* <ins>Live Fuel Moisture Content tiles</ins>:

*"sinusoidal"*: information on the projection of the file.

*"lfmc_median"*: median of the 40 Live Fuel Moisture Content values corresponding to the 40 most similar spectra in the Look-Up Table (see Yebra et al. 2018 for further details).

*"lfmc_stdv"*: standard deviation of the 40 Live Fuel Moisture Content values corresponding to the 40 most similar spectra in the Look-Up Table (see Yebra et al. 2018 for further details).

*"quality_mask"*: 0 if all the reflectance bands from MODIS MCD43A4 used by the algorithm has BRDF_Albedo_Band_Mandatory_Quality_Band classified as good (full BRDF inversions), 1 if any of the bands belongs to a different quality category.

* <ins>Live Fuel Moisture Content mosaics</ins>:

*"lfmc_median"*: median of the 40 Live Fuel Moisture Content values corresponding to the 40 most similar spectra in the Look-Up Table (see Yebra et al. 2018 for further details).

*"lfmc_stdv"*: standard deviation of the 40 Live Fuel Moisture Content values corresponding to the 40 most similar spectra in the Look-Up Table (see Yebra et al. 2018 for further details).

*"quality_mask"*: 0 if all the reflectance bands from MODIS MCD43A4 used by the algorithm has BRDF_Albedo_Band_Mandatory_Quality_Band classified as good (full BRDF inversions), 1 if any of the bands belongs to a different quality category.


