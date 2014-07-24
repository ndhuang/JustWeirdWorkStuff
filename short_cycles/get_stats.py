import os, glob
import pickle
import numpy as np
import matplotlib
from matplotlib import pyplot as pl
from sptpol_software.data.readout import SPTDataReader
from sptpol_software.util.time import SptDatetime

# for zero processing, fridge temps don't have string keys, just indices
# Here's the mapping we need
fridge_inds = {'uc_head': (0, 0), 'ic_head': (0, 1), 'ic_pump': (0, 5),
               'uc_stage': (0, 10), 'ic_stage': (0, 11), 'ic_switch': (0, 8),
               'he4_pump': (0, 4), 'he4_switch': (0, 7), 
               'heat_exchanger': (0, 2), 'uc_switch': (0, 9), 
               'uc_pump': (0, 6), 'mainplate': (0, 3), '4k_head': (0, 12),
               '4k_shield': (0, 13), '50k_shield': (0, 14), 
               '50k_head': (0, 15)}

def readInterval(interval, data = None):
    start = interval[0]
    stop = interval[1]
    if data is None:
        data = SPTDataReader(start, stop, 
                             master_configfile = 
                             "sptpol_stripped_master_config",
                             quiet = True)
    data.readData(start, stop, correct_global_pointing = False,
                  standardize_samplerates = False, unlimited_time = True,
                  zero_processing = True)
    return data

def getCycleTimes(cycle_str, cycle_dir = '/home/sptdat/public_html/data_quality/fridge_cycles/'):
    cycle_stats = open(os.path.join(cycle_dir, cycle_str, 'cycle_stats.txt'))
    cycle_stats.readline() # skip the comment line
    stats = cycle_stats.readline().split()
    return (stats[0], stats[1])

def getFullHold(cycle_str, cycle_dir = '/home/sptdat/public_html/data_quality/fridge_cycles/'):
    cycle_stats = open(os.path.join(cycle_dir, cycle_str, 'cycle_stats.txt'))
    cycle_stats.readline() # skip the comment line
    stats = cycle_stats.readline().split()
    return (stats[1], stats[2]), stats[4]

def getHe4HoldIndices(data):
    hex = data.hk.fridge_temp[0][fridge_inds['heat_exchanger'][1]]
    start_index = 0
    for i, T in enumerate(hex):
        if start_index == 0 and T <= .992:
            start_index = i
        elif start_index > 0 and np.mean(np.diff(hex[i - 10:i])) > 1e-5:
            stop_index = i
            break
    return start_index, stop_index
            
def grabAndAdd(data, key):
    med_temp = np.median(data.hk.fridge_temp[0][fridge_inds[key][1]])
    return {key: med_temp}

def grabData(data, regs):
    out = {}
    if not isinstance(regs, dict):
        if isinstance(regs, str):
            key = regs
            med_val = np.median(data[regs])
            max_val = np.max(data[regs])
            min_val = np.min(data[regs])
            out.update({key: [min_val, med_val, max_val]})
        elif isinstance(regs[0], int):
            key = regs[1]
            med_val = np.median(data[regs[0]])
            max_val = np.max(data[regs[0]])
            min_val = np.min(data[regs[0]])
            out.update({key: [min_val, med_val, max_val]})
        else:
            for r in regs:
                if isinstance(r, str):
                    key = r
                    med_val = np.median(data[r])
                    max_val = np.max(data[r])
                    min_val = np.min(data[r])
                    out.update({key: [min_val, med_val, max_val]})
                elif isinstance(r[0], int):
                    key = r[1]
                    med_val = np.median(data[r[0]])
                    max_val = np.max(data[r[0]])
                    min_val = np.min(data[r[0]])
                    out.update({key: [min_val, med_val, max_val]})
                else:
                    raise RuntimeError("How did I get here?! %s" %str(r))
        return out
    for r in regs.keys():
        out.update(grabData(data[r], regs[r]))
    return out

if __name__ == '__main__':
    regs_to_get = {'array': ['wea_airtemp', 'wea_windspeed', 'wea_winddir'],
                   'hk': {'fridge_temp': {0: [(0, 'uc head'), 
                                              (1, 'ic head'), 
                                              (2, 'hex'), 
                                              (3, 'mainplate'), 
                                              (12, '4K head'), 
                                              (13, '4K shield'), 
                                              (14, '50K shield'), 
                                              (15, '50K head')],
                                          1: (4, 'secondary')}},
                   'antenna': {'scu_temp': [(20, 'cabin temp'),
                                            (21, 'jack 1')],
                               'track_actual': (0, 'Azimuth')}}
    OUTFILE = 'cycle_stats_minmax.pkl'
    out_dict = {}
    borked_file = open('borked_reads.txt', 'w')
    # grab the relevant cycles
    # cycle_dirs = glob.glob('/home/sptdat/public_html/data_quality/fridge_cycles/201404*') + glob.glob('/home/sptdat/public_html/data_quality/fridge_cycles/201405*')
    cycle_dirs = glob.glob('/home/sptdat/public_html/data_quality/fridge_cycles/20140[6-7]*')
    cycles = [os.path.basename(cd) for cd in cycle_dirs]
    cycles = sorted(cycles)
    # hold_keys = ['ic_head', 'uc_head', '4k_shield', '4k_head']
    
    for c in cycles:
        if not out_dict.has_key(c):
            out_dict[c] = {}
        # now get data for the hold time
        interval, hold_time = getFullHold(c)
        try:
            data = readInterval(interval)
        except Exception, err:
            borked_file.write(str(interval) + '\n')
            print interval
            print err

        out_dict[c] = grabData(data, regs_to_get)
        out_dict[c]['hold time'] = hold_time
        #     out_dict[c].update(grabAndAdd(data, key))
        # cabin_temp = np.median(data.antenna.scu_temp[20])
        # out_dict[c]['cabin_temp'] = cabin_temp

        # read in data for the cycle
        interval = getCycleTimes(c)
        try:
            data = readInterval(interval)
        except Exception, err:
            borked_file.write(str(interval) + '\n')
            print interval
            print err

        start, stop = getHe4HoldIndices(data)
        hold_time = (data.hk.fridge_utc[stop] - data.hk.fridge_utc[start]) * 24 * 60
        hex_med = np.median(data.hk.fridge_temp[0][fridge_inds['heat_exchanger'][1]][start:stop])
        out_dict[c]['he4 hold'] = hold_time
        out_dict[c]['hex hold'] = hex_med


    f = open(OUTFILE, 'w')
    pickle.dump(out_dict, f)
    f.close()
