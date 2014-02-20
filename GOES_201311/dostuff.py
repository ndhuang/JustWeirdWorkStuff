import sys
import cPickle as pickle
from matplotlib import mlab
import numpy as np
from sptpol_software.data.readout import SPTDataReader
from sptpol_software.analysis.processing import getGoodBolos
from sptpol_software.util.time import SptDatetime
import IPython

def psdAndCoadd(data, NFFT = 64 * 1024, good_bolos = None):
    psd = np.zeros((NFFT / 2,))
    if good_bolos is None:
        good_bolos = data.rec.bolo_ids
    for bolo in good_bolos:
        p, freq = data.bolodata[bolo].psd(NFFT = NFFT)
        psd += p
    psd /= len(good_bolos)
    return psd, freq
    
if __name__ == '__main__':
    from local_config import *
    for t in good_times:
        data = SPTDataReader(start_date = SptDatetime(t[0]), stop_date = SptDatetime(t[1]), quiet = True)
        data.readData(correct_global_pointing = False, quiet = True)
        good_bolos = getGoodBolos(data, good_bolos = ['calibrator', 'elnod', 'flagged'])
        if len(good_bolos) < 10:
            raise RuntimeError('We\'s fucked up the cuts!')
        
        # coadd timestreams
        good_ids = data.rec.boloListToIndex(good_bolos)
        coadd = np.mean(data.bolodata_array[good_ids], 0)
        # coadd = None
        # for gb in good_bolos:
        #     if coadd is None:
        #         coadd = data.bolodata[gb]
        #     else:
        #         coadd += data.bolodata[gb]
        # coadd /= len(good_bolos)
        psd, freq = mlab.psd(coadd, NFFT = 2*1024, Fs = 1. / data.bolodata[0].timestep, window = mlab.window_hanning, detrend = mlab.detrend_linear)
        f = open('coaddfirst/lowres100mHz/' + t[2] + '_ ' + t[0].replace(' ', '_') + '.pkl', 'w')
        pickle.dump([psd, freq], f)
        f.close()
        # psd, freq = psdAndCoadd(data, good_bolos = good_bolos)
        # f = open('good/' + t[2] + '_ ' + t[0].replace(' ', '_') + '.pkl', 'w')
        # pickle.dump([psd, freq], f)
        # f.close()
                                  
        
