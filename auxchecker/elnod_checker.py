#!/usr/bin/python
import os
from os import path
from multiprocessing import Process, RLock
import numpy as np
import sptpol_software.util.files as files

def checkOb(obfile, check_field, lock = None):
    # return True if the ob is bad
    try:
        ob = files.read(obfile)
    except ValueError:
        return False
    unique_vals = np.unique(ob.observation[check_field])
    unique_frac = float(len(unique_vals)) / len(ob.observation[check_field])
    if unique_frac < 1.2:
        lock.acquire()
        res_str = ob.from_filename + ' ' + str(unique_frac)
        # for v in unique_vals:
        #     res_str += ', ' + str(v)
        print res_str
        lock.release()
        return True

def check_elnods(elnod_auxdata_dir = 
                 path.abspath('/data/sptdat/auxdata/elnod/'), num_procs = 6):
    lock = RLock()
    elnod_files = sorted([path.join(elnod_auxdata_dir, elnod_file) for 
                       elnod_file in os.listdir(elnod_auxdata_dir)])

    j = 0
    while j < len(elnod_files):
        procs = [[] for i in range(num_procs)]
        for i in range(num_procs):
            if j >= len(elnod_files):
                break
            procs[i] = Process(target = checkOb, 
                               args = (elnod_files[j], 'bolo_elnod_response',
                                       lock))
            procs[i].start()
            j += 1

        for p in procs:
            p.join()

if __name__ == '__main__':
    check_elnods()
