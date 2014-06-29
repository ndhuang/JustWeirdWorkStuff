import cPickle as pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as pl
from sptpol_software.autotools import logs
from sptpol_software.data.readout import SPTDataReader
import scan_stacker as ss

def getTurnarounds(data):
    '''
    Returns a list of lists of indices which point to the turnarounds
    Assumes the scans begin exactly at the beginning of the data
    '''
    starts = np.zeros(len(data.scan) + 1, dtype = int)
    stops = np.zeros(len(data.scan) + 1, dtype = int)
    for i, scan in enumerate(data.scan):
        starts[i + 1] = scan.start_index
        stops[i] = scan.stop_index
        
    inds = np.array([])
    for start, stop in zip(starts, stops):
        inds = np.concatenate((inds, np.arange(start, stop)))

    return inds.astype(int)

def readInterval(interval):
    '''Just read some data'''
    data = SPTDataReader(interval[0], interval[1], quiet = True)
    data.readData(interval[0], interval[1],
                  # options we may want to use
                  correct_global_pointing = False,
                  standardize_samplerates = False)
    return data

if __name__ == '__main__':
    # source = 'ra5h30dec-55'
    # start = '140429 12:46:09'
    # end = '140429 13:23:12'
    # intervals = logs.readSourceScanTimes(start, end, source, nscans_min = 2)
    f = open('/home/ndhuang/spt_code/sptpol_software/scratch/ndhuang/scan_maker/az_tests.pkl')
    intervals = pickle.load(f)
    f.close()
    intervals = intervals['normal']
    for i, inter in enumerate(intervals):
        data = readInterval(inter)
        t = np.arange(len(data.antenna.track_actual[0]), dtype = float) / 100
        az_err = data.antenna.track_err[0]
        turns = getTurnarounds(data)
        # az, n  = ss.stack(data.antenna.track_actual[0], 2)
        # az_err = ss.makeStacks(data.antenna.track_err[0], 2, n)
        pl.figure()
        # pl.subplot(211)
        # pl.plot(t, az)
        # pl.title('Az')
        # pl.ylabel('Az (degrees)')
        
        # pl.subplot(212)
        pl.plot(t[data.scan[0].scan_slice], az_err[data.scan[0].scan_slice])
        # pl.plot(t[turns], az_err[turns], '.k')
        pl.title('Az Error')
        pl.ylabel('Error (degrees)')
        pl.xlabel('Time (s)')

        pl.savefig('/home/ndhuang/plots/scan_profiles/az/%d.png' %i)
