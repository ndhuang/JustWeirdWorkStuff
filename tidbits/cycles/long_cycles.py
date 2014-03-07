from sptpol_software.data.readout import SPTDataReader

from pylab import *

from os import path
import os, sys

def mkPlot(data, start):
    figure()
    subplot(311)
    plot(data.hk.fridge_utc, data.hk.fridge_temp.uc_stage)
    title('UC')

    subplot(312)
    plot(data.hk.fridge_utc, data.hk.fridge_temp.ic_stage)
    title('IC')
    
    subplot(313)
    plot(data.hk.fridge_utc, data.hk.fridge_temp.heat_exchanger)
    title('HEX')
    savefig(start + '.png')

def getTimes(dqdir = '/home/sptdat/public_html/data_quality/fridge_cycles'):
    subds = sorted(os.listdir(dqdir))[-12:]
    for s in subds:
        f = open(path.join(dqdir, s, 'cycle_stats.txt'))
        stats = f.readlines()[1].split()
        start = stats[0]
        end = stats[1]
        data = SPTDataReader(start, end, 
                             master_configfile = 'sptpol_stripped_master_config')
        data.readData(correct_global_pointing = False, process_psds = False)
        mkPlot(data, start)

if __name__ == '__main__':
    getTimes()
