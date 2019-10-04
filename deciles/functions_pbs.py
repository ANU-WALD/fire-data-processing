import os
import subprocess
import time


def generate_pbs(pbs_path_file, q, ncpus, mem, walltime_hr, cmd_list):

    if os.path.exists(pbs_path_file):
        os.remove(pbs_path_file)

    with open(pbs_path_file, 'a') as f:
        f.write('#!/bin/bash\n')
        f.write('#PBS -P xc0\n')
        f.write('#PBS -q ' + q + '\n')
        f.write('#PBS -l ncpus=' + str(ncpus) + '\n')
        f.write('#PBS -l mem=' + str(mem) + 'GB\n')
        f.write('#PBS -l walltime=' + str(walltime_hr).zfill(2) + ':00:00\n')
        for cmd_item in cmd_list:
            f.write(cmd_item + '\n')


def schedule_pbs(pbs_path, pbs_dict, steps, ids_path_file):

    for step in steps:
        generate_pbs(pbs_path_file=pbs_path + pbs_dict[step]['config']['pbs_file'],
                     q=pbs_dict[step]['config']['q'],
                     ncpus=pbs_dict[step]['config']['ncpus'],
                     mem=pbs_dict[step]['config']['mem'],
                     walltime_hr=pbs_dict[step]['config']['walltime_hr'],
                     cmd_list=pbs_dict[step]['cmd_list'])

    if os.path.exists(ids_path_file):
        os.remove(ids_path_file)
    os.chdir(pbs_path)
    with open(ids_path_file, 'a') as f:
        pbs_ids = {}
        for step in steps:
            pbs_path_file = pbs_path + pbs_dict[step]['config']['pbs_file']

            dep_step = pbs_dict[step]['depends_on']
            if dep_step is None:
                pbs_id = subprocess.check_output(['qsub', pbs_path_file]).decode("utf-8").rstrip()
                pbs_ids[step] = pbs_id
            else:
                pbs_id = subprocess.check_output(['qsub', '-W depend=afterany:' + pbs_ids[dep_step], pbs_path_file]).decode("utf-8").rstrip()
                pbs_ids[step] = pbs_id
            f.write(pbs_path_file + ' : ' + pbs_id + '\n')
            time.sleep(1)
