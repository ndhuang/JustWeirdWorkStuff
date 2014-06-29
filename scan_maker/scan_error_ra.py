import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as pl
from sptpol_software.autotools import logs
from sptpol_software.data.readout import SPTDataReader
import util

def readInterval(interval):
    '''Just read some data'''
    interval = logs.readSourceScanTimes(interval[0], interval[1],
                                        source, nscans_min = 50)[0]
    data = SPTDataReader(interval[0], interval[1], quiet = True, 
                         config_file = "sptpol_stripped_master_config")
    data.readData(interval[0], interval[1],
                  correct_global_pointing = False,
                  standardize_samplerates = False)
    return data

def doTheStuff(data, savedir, savename):
    left = [s.is_leftgoing for s in data.scan]
    right = np.bitwise_not(left)
    az_err = np.asarray([np.zeros(s.stop_index - s.start_index) 
                         for s in data.scan])
    ra = np.asarray([np.zeros(s.stop_index - s.start_index) 
                         for s in data.scan])
    for i, s in enumerate(data.scan):
        az_err[i] = -data.antenna.track_err[0][s.scan_slice]
        ra[i] = data.antenna.ra[s.scan_slice]
    az_r = np.concatenate([np.asarray(a) for a in az_err[right]])
    az_l = np.concatenate([np.asarray(a) for a in az_err[left]])
    ra_r = np.concatenate([np.asarray(a) for a in ra[right]])
    ra_l = np.concatenate([np.asarray(a) for a in ra[left]])
    
    pl.figure()
    pl.subplot(211)
    pl.plot(ra_r, az_r, 'k.')
    pl.title('Az Error, right-going')
    pl.ylabel('Az Error (degrees)')
    pl.subplot(212)
    pl.plot(ra_l, az_l, 'k.')
    pl.title('Az Error, left-going')
    pl.ylabel('Az Error (degrees)')
    pl.xlabel('RA (degrees)')
    pl.savefig(os.path.join(savedir, savename + '_all.png'))
    pl.close()

    right_bins = util.bin1d(ra_r, delta_x = 10. / 60)
    left_bins = util.bin1d(ra_l, delta_x = 10. / 60)
    az_rbin = util.mapToBins(az_r, right_bins)
    az_lbin = util.mapToBins(az_l, left_bins)
    ra_rbin = util.mapToBins(ra_r, right_bins)
    ra_lbin = util.mapToBins(ra_l, left_bins)

    pl.figure()
    pl.plot(ra_rbin, az_rbin, label = 'right-going')
    pl.plot(ra_lbin, az_lbin, label = 'left-going')
    pl.title('Az Error vs RA')
    pl.ylabel('Az Error (degrees)')
    pl.xlabel('RA (degrees)')
    pl.savefig(os.path.join(savedir, savename + '_binned.png'))
    pl.close()

if __name__ == '__main__':
    source = 'ra0hdec-57.5'
    times = [['140525 05:01:19', '140525 07:40:23'], # fast scan, new prof
             ['140406 15:23:56', '140406 18:03:27'], # fast scan, old prof
             ['140328 10:26:20', '140328 12:57:40'], # slow scan, 2013 l-t
             ['140526 02:42:21', '140526 07:04:26']] # recent 2013 l-t
    names = ['fast_new_prof', 'fast_old_prof', 'older_lt', 'recent_lt']
    datas = []
    for name, interval in zip(names, times):
        data = readInterval(interval)
        datas.append(data)
        # doTheStuff(data, '/home/ndhuang/plots/az_error', name)
