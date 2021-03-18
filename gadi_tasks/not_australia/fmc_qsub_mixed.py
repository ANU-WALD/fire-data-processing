import os
from datetime import datetime, timedelta

def daterange(start_date, end_date, time_step): 
    n = 0
    while True:
        d = start_date + timedelta(days=n)
        if d > end_date:
            break
        n += time_step  # time range needed (in days)
        yield d



tiles = ['h20v05','h20v06']
dates = daterange(datetime(2018,7,1),datetime(2018,10,31),1)


if __name__ == "__main__":
    for tile in tiles:
        for date in dates:
            print("qsub -v 'year={0},tile={1}' /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/not_australia/fmc_mixed.qsub".format(date.strftime('%Y%m%d'), tile))
            os.system('qsub -v "year={0},tile={1}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/not_australia/fmc_mixed.qsub'.format(date.strftime('%Y%m%d'), tile))
