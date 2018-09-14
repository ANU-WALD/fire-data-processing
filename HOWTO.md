qsub -I -P xc0 -q normal -l walltime=2:00:00,mem=1GB,ncpus=1,jobfs=50GB -l wd

/g/data1/xc0/software/conda-envs/rs3/bin/python update_fmc.py -t h32v10 -d 20180101 -tmp $PBS_JOBFS -dst /g/data/fj4/scratch/2018/test.nc

/g/data1/xc0/software/conda-envs/rs3/bin/python update_fmc.py -t h32v10 -d 2018 -tmp $PBS_JOBFS -dst /g/data/fj4/scratch/2018/test.nc
