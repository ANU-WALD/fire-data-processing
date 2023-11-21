import os

if __name__ == "__main__":
    for y in [2010,2015]:
        print(y)
        os.system('qsub -v "y={0}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_one_time_qsubs/zonalstats_rank_with_deciles.qsub'.format(y))
