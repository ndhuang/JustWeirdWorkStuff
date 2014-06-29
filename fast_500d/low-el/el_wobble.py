import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import mlab, pyplot as pl
from sptpol_software.autotools import logs
from sptpol_software.data.readout import SPTDataReader
from sptpol_software.analysis.processing import getGoodBolos

if __name__ == '__main__':
    # start = '140611 06:03:43' # new fast scan
    # stop = '140611 08:42:36'
    start = '140325 02:54:31' # lead-trail
    stop = '140325 08:47:35'
    start, stop = logs.readSourceScanTimes(start, stop, 'ra0hdec-57.5', 
                                           nscans_min = 30)[0]
    data = SPTDataReader(start, stop, quiet = True)
    data.readData(start, stop, correct_global_pointing = False)
    scan_len = [(s.stop_index - s.start_index) for s in data.scan]
    scan_len = max(scan_len)
    coadd = [np.zeros(scan_len), np.zeros(scan_len)]
    coadd_el = [np.zeros(scan_len), np.zeros(scan_len)]
    coadd_err = [np.zeros(scan_len), np.zeros(scan_len)]
    nfft = 2048
    pxx = [np.zeros(nfft / 2 + 1), np.zeros(nfft / 2 + 1)]
    pxx_el = [np.zeros(nfft / 2 + 1), np.zeros(nfft / 2 + 1)]
    pxx_err = [np.zeros(nfft / 2 + 1), np.zeros(nfft / 2 + 1)]
    good_bolos = getGoodBolos(data, 'map_default')
    for s in data.scan:
        if s.is_leftgoing:
            ind = 0
        else:
            ind = 1
        scan_el = data.antenna.track_actual[1][s.scan_slice]
        scan_err = data.antenna.track_err[1][s.scan_slice]
        pxx_el[ind] += mlab.psd(scan_el, NFFT = nfft, 
                                Fs = data.header.samplerate)[0]
        pxx_err[ind] += mlab.psd(scan_err, NFFT = nfft, 
                                Fs = data.header.samplerate)[0]
        coadd_el[ind] += np.concatenate((scan_el, np.zeros(len(coadd_el[ind]) -
                                                           len(scan_el))))
        coadd_err[ind] += np.concatenate((scan_err, 
                                          np.zeros(len(coadd_err[ind]) -
                                                   len(scan_err))))
        for b in good_bolos:
            b = data.bolodata[b]
            scan = b[s.scan_slice]
            pxx[ind] += mlab.psd(scan, NFFT = nfft,
                                 Fs = data.header.samplerate)[0]
            coadd[ind] += np.concatenate((scan, np.zeros(len(coadd[ind]) - 
                                                          len(scan))))

    pxxc = [[], []]
    pxxc_el = [[], []]
    pxxc_err = [[], []]
    for i, dat in enumerate(coadd):
        pxxc[i] = mlab.psd(dat, NFFT = nfft, Fs = data.header.samplerate)[0]
        pxxc_el[i] = mlab.psd(coadd_el[i], NFFT = nfft, 
                              Fs = data.header.samplerate)[0]
        pxxc_err[i] = mlab.psd(coadd_err[i], NFFT = nfft, 
                              Fs = data.header.samplerate)[0]
    freq = np.linspace(0, data.header.samplerate, nfft / 2 + 2)[1:]

    savedir = '/home/ndhuang/plots/fast-500d/el_wobble/lead-trail/'

    pl.figure()
    pl.loglog(freq, pxx[0], label = 'PSD first')
    pl.loglog(freq, pxxc[0], label = 'PSD Second')
    pl.title('PSD of left-going stacked scans')
    pl.ylabel('PSD Units?')
    pl.xlabel('Frequency (Hz)')
    pl.vlines(2.4, pl.ylim()[0], pl.ylim()[1], linestyle = 'dashed')
    pl.legend()
    pl.savefig(os.path.join(savedir, 'left.png'))
    pl.close('all')

    pl.figure()
    pl.loglog(freq, pxx[1], label = 'PSD first')
    pl.loglog(freq, pxxc[1], label = 'PSD Second')
    pl.title('PSD of right-going stacked scans')
    pl.ylabel('PSD Units?')
    pl.xlabel('Frequency (Hz)')
    pl.vlines(2.4, pl.ylim()[0], pl.ylim()[1], linestyle = 'dashed')
    pl.legend()
    pl.savefig(os.path.join(savedir, 'right.png'))
    pl.close('all')

    # plot el
    pl.figure()
    pl.loglog(freq, pxx_el[0], label = 'PSD first')
    pl.loglog(freq, pxxc_el[0], label = 'PSD Second')
    pl.title('PSD of el in left-going scans')
    pl.ylabel('PSD Units?')
    pl.xlabel('Frequency (Hz)')
    pl.vlines(2.4, pl.ylim()[0], pl.ylim()[1], linestyle = 'dashed')
    pl.legend()
    pl.savefig(os.path.join(savedir, 'left_el.png'))
    pl.close('all')

    pl.figure()
    pl.loglog(freq, pxx_el[1], label = 'PSD first')
    pl.loglog(freq, pxxc_el[1], label = 'PSD Second')
    pl.title('PSD of el in right-going scans')
    pl.ylabel('PSD Units?')
    pl.xlabel('Frequency (Hz)')
    pl.vlines(2.4, pl.ylim()[0], pl.ylim()[1], linestyle = 'dashed')
    pl.legend()
    pl.savefig(os.path.join(savedir, 'right_el.png'))
    pl.close('all')

    # plot err
    pl.figure()
    pl.loglog(freq, pxx_err[0], label = 'PSD first')
    pl.loglog(freq, pxxc_err[0], label = 'PSD Second')
    pl.title('PSD of el error in left-going scans')
    pl.ylabel('PSD Units?')
    pl.xlabel('Frequency (Hz)')
    pl.vlines(2.4, pl.ylim()[0], pl.ylim()[1], linestyle = 'dashed')
    pl.legend()
    pl.savefig(os.path.join(savedir, 'left_err.png'))
    pl.close('all')

    pl.figure()
    pl.loglog(freq, pxx_err[1], label = 'PSD first')
    pl.loglog(freq, pxxc_err[1], label = 'PSD Second')
    pl.title('PSD of el error in right-going scans')
    pl.ylabel('PSD Units?')
    pl.xlabel('Frequency (Hz)')
    pl.vlines(2.4, pl.ylim()[0], pl.ylim()[1], linestyle = 'dashed')
    pl.legend()
    pl.savefig(os.path.join(savedir, 'right_err.png'))
    pl.close('all')
