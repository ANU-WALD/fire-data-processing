import subprocess
import time
import os

pwd = os.getcwd()
python_exe = '/g/data/xc0/software/python/miniconda3/bin/python3'
python_fun = pwd + '/' + 'function_calc_decile_for_tile.py'


def calc_dec_concurrent(tile_path_files):
    print('in calc dec concurrent')

    proc_dict = {}

    while len(tile_path_files) > 0 or len(proc_dict) > 0:

        del_list = []
        for pid, proc in proc_dict.items():
            if proc.poll() is not None:
                del_list.append(pid)

        for del_pid in del_list:
            del proc_dict[del_pid]
            print('>>>>', len(proc_dict.keys()), proc_dict.keys(), len(tile_path_files))

        if len(proc_dict.keys()) < 6 and len(tile_path_files) > 0:
            # select on path_file and run the command for it
            tile_path_file = tile_path_files[0]
            tile_file = os.path.basename(tile_path_file)
            tile_path = os.path.dirname(tile_path_file)

            tile_dc_path = tile_path + '/' + 'deciles'

            if not os.path.exists(tile_dc_path):
                os.mkdir(tile_dc_path)

            tile_dc_file = tile_file.replace('.pk', '_dc.pk')
            tile_dc_path_file = tile_dc_path + '/' + tile_dc_file

            tile_path_files.pop(0)
            if not os.path.exists(tile_dc_path_file):
                item_proc = subprocess.Popen([python_exe, python_fun, tile_path_file], shell=False)
                # time.sleep(0.5)
                proc_dict[item_proc.pid] = item_proc
                print('>>>>', len(proc_dict.keys()), proc_dict.keys(), len(tile_path_files))
        # else:
        #     time.sleep(0.5)
