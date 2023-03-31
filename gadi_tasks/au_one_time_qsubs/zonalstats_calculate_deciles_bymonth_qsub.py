import os

if __name__ == "__main__":
    for m in range(12,13):
        print(m)
        os.system('qsub -v "m={0}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_one_time_qsubs/zonalstats_calculate_deciles_bymonth.qsub'.format(m))
