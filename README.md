##### Fire Data Processing Repository
# ANU-WALD

The Fire Data Processing repository is a collection of scripts used to produce the fuel moisture and flammability data for usage on the online interactive [Australian Flammability Monitoring system (AFMS)](http://wenfo.org/afms/).

This is a research initiative to provide quality spatial information on fire hazards in Australia to better understand the risk of bushfires, their severity and preparing ways to respond to them.


### Authors
---
* *[Zac Hatfield Dodds](https://github.com/Zac-HD) and [Dion Misic](https://github.com/kingdion)* (code)
* *[Marta Yebra](https://researchers.anu.edu.au/researchers/yebra-m)* (science)

### Important Links
---
* [The Project](http://www.bnhcrc.com.au/research/understanding-mitigating-hazards/255)
* [ANU Water and Landscape Dynamics Group](http://www.wenfo.org/wald/)
* [Australian Flammability Monitoring System](http://wenfo.org/afms/)
* [Australian Environment Explorer](http://wenfo.org/ausenv/)


### Scripts
---
#### General Usage
All scripts accept a help argument which displays all input flags. Use "python script.py --help" on the respective script to display help.

You must be in the following NCI project groups to perform certain tasks with these scripts;

* **ub8** - Data Access (**ub8_admin** for write permissions)
* **xc0** - To schedule Raijin jobs & edit scripts

Alternatively, you could edit the various \*.qsub files to run under a different project's Raijin allocation.

As a general use-case, you should be in the *root* directory of the repository to run scripts.

---

#### onetile.py
Onetile is used to generate *one tile* of live fuel moisture content (LFMC) data for the [AFMS](http://wenfo.org/afms/) system. The script uses a group of colour channels within satellite data from [NASA's MODIS satellite](https://terra.nasa.gov/about/terra-instruments/modis) (sinusoidal projection) to calculate information about fuel moisture and reflectance on a specific tile of the world.

Onetile is optionally capable of interpreting SPOT6 and SPOT7 satellite data and can be extended to support more.

The world map on the sinusoidal projection grid can be found below. ![Sinusoidal Projection Grid World Map](https://modis-land.gsfc.nasa.gov/images/MODIS_sinusoidal_grid1.gif).

#### launchmany.py
Launchmany is essentially a job queue system for the NCI Raijin super computer and producing LFMC data. The job queue distributes the input tiles to onetile.py (the heart of the processing) and processes each tile individually to derive LFMC data.

As input, this script takes a comma separated list of sinusoidal tiles and schedules a set of jobs on Raijin (using the Raijin specific job handler). Automating this LFMC process is appealing as generating multiple tiles over many years can take some time.

For ease of use, launchmany has a few tile shortcuts builtin for countries around the world, such as Australia, Spain and South Africa.

#### modis.py
This script provides general-purpose functions for manipulating MODIS data, including loading reflectance and restoring physical coordinates to an array for a given tile.

#### mosaic.py
Mosaic is used to reproject the MODIS fuel moisture sinusoidal grid of Australia to a WGS84 Lat/Lon coordinate mosaic. This script also calculates and adds a flammability variable to the the standard set of data. In addition to reprojecting, this script can be used to combine tiles.
