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
All scripts accept a help argument which displays all input flags. Use "python script.py --help" on the respective script to display help.

You must be in the following NCI project groups to perform certain tasks with these scripts;

* **ub8** - Data Access (**ub8_admin** for write permissions)
* **xc0** - To activate a Python environment with all the required packages
* A project with Gadi allocation, to edit and run the various \*.qsub files


#### Dependencies
These scripts rely on a range of scientific packages not included in the Python standard library.
If you are a member of the xc0 group on NCI, simply run "source activate rs3" to activate an environment with all the requirements.
(If this does not work, see /g/data/xc0/software/README.xc0-miniconda)

To create your own environment, run the command:

    conda create --name rs3 --channel conda-forge python=3 xarray>=0.10 pynio jupyter

If that doesn't work (eg due to package updates), install from `environment.yml` to get *exactly* the same packages.


#### Pipeline Explained
The core scripts and files are in the folder **"main\_lfmc\_flam"**.
* "FMC.npy" and "LUT.npy" compose the lookup table used to match reflectance data to Live Fuel Moisture Content values.
* "nc_metadata.json" contains the metadata copied into the LFMC and flammability netCDF files.
* "update\_fmc.py" is used to create or update (if already existing) the LFMC tiles starting from MCD43A4 reflectance data and MCD12Q1 IGBP land cover data. It can be run, for example, using the following command:

    module load cdo
    /g/data/xc0/software/conda-envs/rs3/bin/python update\_fmc.py -d 2023 -t h27v11 -dst /g/data/ub8/au/FMC/tiles/fmc\_c6\_2023\_h27v11.nc -tmp /g/data/ub8/au/FMC/tmp/

* "update\_fmc\_mosaic.py" creates or updates (if already existing) the LFMC mosaics. It can be run, for example, using the following command:

    module load cdo
    /g/data/xc0/software/conda-envs/rs3/bin/python update\_fmc\_mosaic.py -y 2023 -dst /g/data/ub8/au/FMC/mosaics/fmc\_c6\_2023.nc -tmp /g/data/ub8/au/FMC/tmp/

* "cdo_mean.py" is used to generate mean LFMC values tiles used to retrieve flammability data.
* "update\_flammability.py" is used to generate or update (if already existing) the flammability tiles using the LFMC tiles and mean LFMC values tiles as starting point. It can be run, for example, using the following command:

    module load cdo
    /g/data/xc0/software/conda-envs/rs3/bin/python update\_flammability.py -y 2023 -t h32v11 -dst /g/data/ub8/au/FMC/tiles/flam\_c6\_2023\_h32v11.nc -tmp /g/data/ub8/au/FMC/tmp/

* "update\_flammability\_mosaic.py" creates or updates (if already existing) the flammability mosaics. It can be run, for example, using the following command:

    module load cdo
    /g/data/xc0/software/conda-envs/rs3/bin/python update\_flammability\_mosaic.py -y 2023 -dst /g/data/ub8/au/FMC/mosaics/flam\_c6\_2023.nc -tmp /g/data/ub8/au/FMC/tmp/

* "utils.py" contains functions employed in the other scripts.
* "update\_fmc\_flam.sh" is a shell script that can be used to update all the LFMC and flammability tiles and their mosaics. It can be run, for example, using the following command:

    cd ./fire-data-processing/main\_lfmc\_flam/
    chmod +x ./update\_fmc\_flam.sh
    ./update\_fmc\_flam.sh

* "ALTERNATIVE\_update\_fmc\_different\_mcd43a4\_path.py" and "ALTERNATIVE\_update\_fmc\_every8days.py" are variants of the main scripts that can be used if the directory to MODIS tiles is different or if needed to create 8-daily LFMC tiles.




