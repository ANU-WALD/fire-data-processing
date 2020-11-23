import os


if __name__ == "__main__":
    os.system('qsub -v "year=2013,tile=h09v04" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_calif.qsub')
    os.system('qsub -v "year=2014,tile=h08v05" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/fmc_calif.qsub')
