import os

if __name__ == "__main__":
    for var in ['fmc','flam']:
        for area in ['fwa']: #['fwa','lga']
            os.system('qsub -v "area={0}, var={1}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_recurrent_qsubs/zonal_stats_rel_rec.qsub'.format(area, var))
            os.system('qsub -v "area={0}, var={1}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_recurrent_qsubs/zonal_stats_abs_rec.qsub'.format(area, var))

