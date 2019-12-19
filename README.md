## Fire Data Processing -- ANU-WALD

The Fire Data Processing repository is a collection of scripts used to produce the fuel moisture and flammability data for usage on the online interactive [Australian Flammability Monitoring system (AFMS)](http://wenfo.org/afms/).

This is a research initiative to provide quality spatial information on fire hazards in Australia to better understand the risk of bushfires, their severity and preparing ways to respond to them.


### Important Links
---
* [The Project](http://www.bnhcrc.com.au/research/understanding-mitigating-hazards/255)
* [ANU Water and Landscape Dynamics Group](http://www.wenfo.org/wald/)
* [Australian Flammability Monitoring System](http://wenfo.org/afms/)
* [Australian Environment Explorer](http://wenfo.org/ausenv/)


### Scripts
---

To create or update the archive, run the following bash commands:

    cd ~/fire-data-processing
    git pull
    source activate rs3
    python launchmany.py


#### General Usage
All scripts accept a help argument which displays all input flags. Use "python script.py --help" on the respective script to display help.

You must be in the following NCI project groups to perform certain tasks with these scripts;

* **ub8** - Data Access (**ub8_admin** for write permissions)
* **xc0** - To schedule Raijin jobs & edit scripts

Alternatively, you could edit the various \*.qsub files to run under a different project's Raijin allocation.

As a general use-case, you should be in the *root* directory of the repository to run scripts.

#### Dependencies
These scripts rely on a range of scientific packages not included in the Python standard library.
If you are a member of the xc0 group on NCI, simply run "source activate rs3" to activate an environment with all the requirements.
(If this does not work, see /g/data/xc0/software/README.xc0-miniconda)

To create your own environment, run the command:

    conda create --name rs3 --channel conda-forge python=3 xarray>=0.10 pynio jupyter

If that doesn't work (eg due to package updates), install from `environment.yml` to get *exactly* the same packages.
