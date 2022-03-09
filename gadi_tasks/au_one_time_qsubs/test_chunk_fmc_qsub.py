import os
import random

number_combinations = 50

if __name__ == "__main__":
    for _ in range(number_combinations):
        tchunk, latchunk, lonchunk = random.randint(1,10)*10, random.randint(1,10)*10, random.randint(1,10)*10
        os.system('cd /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/jobs_reports')
        os.system('qsub -v "tchunk={0},latchunk={1},lonchunk={2}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_one_time_qsubs/test_chunk_fmc.qsub'.format(tchunk, latchunk, lonchunk))


