import os

if __name__ == "__main__":
    for var in ['fmc','flam']:
        os.system('qsub -v "var={0}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_recurrent_qsubs/rank_with_deciles_rec.qsub'.format(var))
