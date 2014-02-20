#!/usr/local/bin/python
from gv_datareader import GoodVibeReader

from sptpol_software.data.readout import SPTDataReader
from SomeTools import bin_func, nextpow2

from datetime import datetime, timedelta

import pylab as pl
import numpy as np
import os, sys
import pickle
import pytz

# sptz = pytz.timezone('Antarctica/South_Pole')
# local = sptz
UTC = pytz.timezone('UTC')
sptz = UTC
local = UTC
datdir = '/data/sptdaq/good_vibrations/parser_output/'
dat_start = sorted([datetime.strptime(d, '%Y%m%d_%H%M%S') 
                    for d in os.listdir(datdir)])
for i, dt in enumerate(dat_start):
    dat_start[i] = sptz.localize(dat_start[i])

def mk_plot(start, end, title, save = False):
    i = 0
    while i < len(dat_start) - 1:
        if dat_start[i] <= start and start < dat_start[i + 1]:
            if dat_start[i + 1] < end:
                raise RuntimeError("Sorry, we can't bridge good " + 
                                   "vibes data files.\n" + 
                                   "%s is between %s and %s" 
                                   %(dat_start[i + 1].astimezone(sptz),
                                     start.astimezone(sptz), 
                                     end.astimezone(sptz)))
            gvdat = GoodVibeReader(dat_start[i].strftime('%Y%m%d_%H%M%S'), 
                                   verbose = False)
            break
        if i == len(dat_start) - 2:
            raise RuntimeError("Sorry, we don't have data from %s yet" 
                               %str(start.astimezone(sptz)))
        i += 1
        
    rxx = gvdat.rxx.get_section(start, end)
    rxy = gvdat.rxy.get_section(start, end)
    optics = gvdat.optics.get_section(start, end)
    all_gv = [rxx, rxy, optics]
    data = SPTDataReader(experiment = 'SPTpol', verbose = False, quiet = True,
                         master_configfile='sptpol_stripped_master_config')
    data.readData(start.astimezone(UTC), end.astimezone(UTC), 
                  verbose = False, quiet = True, 
                  process_psds = False, remove_unknown_bolos=False, 
                  correct_global_pointing = False)

    for b in all_gv:
        b.make_time()
        b.secs_mic = b.mic_t
        b.secs_accel = b.accel_t

    # prep data
    time = data.antenna.track_utc
    elenc1 = data.antenna.track_rawenc[0]
    elenc2 = data.antenna.track_rawenc[1]
    azerr = data.antenna.track_err[0]
    elerr = data.antenna.track_err[1]
    az = data.antenna.track_actual[0]
    el = data.antenna.track_actual[1]
    azrate = data.antenna.track_act_rate[0]
    elrate = data.antenna.track_act_rate[1]
    optics1 = data.antenna.scu_benchact[0]
    optics2 = data.antenna.scu_benchact[1]
    optics3 = data.antenna.scu_benchact[2]

    dt = np.diff(time)
    dt = map(timedelta.total_seconds, dt)
    azacc = np.diff(azrate) / dt
    elacc = np.diff(elrate) / dt

    len_dec = 50
    n_dec = int(np.ceil(float(len(azacc)) / len_dec))
    azacc_dec = np.empty(n_dec)
    elacc_dec = np.empty(n_dec)
    for i in range(n_dec - 1):
        azacc_dec[i] = np.mean(azacc[i * len_dec:(i + 1) * len_dec])
        elacc_dec[i] = np.mean(elacc[i * len_dec:(i + 1) * len_dec])

    azacc_dec[n_dec - 1] = np.mean(azacc[(n_dec - 1) * len_dec:])
    elacc_dec[n_dec - 1] = np.mean(elacc[(n_dec - 1) * len_dec:])    
    
    azacc = azacc_dec
    elacc = elacc_dec
    acc_inds = range(0, len(time), len_dec)
    
    # mic
    sp = 1
    tsp = 12
    fig = pl.figure(figsize = (8, tsp / 3 * 6))
    pl.subplot(tsp, 1, sp, title = 'X Mic')
    pl.plot(rxx.secs_mic, rxx.mic, label = 'rx_x')
    pl.xlim(min(rxx.secs_mic), max(rxx.secs_mic))
    sp += 1

    pl.subplot(tsp, 1, sp, title = 'Y Mic')
    pl.plot(rxy.secs_mic, rxy.mic, label = 'rx_y')
    pl.xlim(min(rxy.secs_mic), max(rxy.secs_mic))
    sp += 1

    # accel
    pl.subplot(tsp, 1, sp, title = 'X Accelerometer')
    pl.plot(rxx.secs_accel, rxx.accel, label = 'rx_x')
    pl.xlim(min(rxx.secs_accel), max(rxx.secs_accel))
    sp += 1

    pl.subplot(tsp, 1, sp, title = 'Y Accelerometer')
    pl.plot(rxy.secs_accel, rxy.accel, label = 'rx_y')
    pl.xlim(min(rxy.secs_accel), max(rxy.secs_accel))
    sp += 1


    # az and el
    pl.subplot(tsp, 1, sp, title = 'Actual Az')
    pl.plot(time, az, label = 'Az')
    sp += 1
    
    pl.subplot(tsp, 1, sp, title = 'Actual El')
    pl.plot(time, el, label = 'El')
    sp += 1

    # acc
    pl.subplot(tsp, 1, sp, title = 'Az Acceleration')
    pl.plot(time[acc_inds], azacc)
    sp += 1

    pl.subplot(tsp, 1, sp, title = 'El Acceleration')
    pl.plot(time[acc_inds], elacc)
    sp += 1

    # tracker errors
    pl.subplot(tsp, 1, sp, title = 'Az and El Error')
    pl.plot(time, azerr, label = 'Az')
    pl.plot(time, elerr, label = 'El')
    pl.legend()
    sp += 1

    # optics bench
    pl.subplot(tsp, 1, sp, title = 'Optics Mic')
    pl.plot(optics.secs_mic, optics.mic, label = 'optics')
    pl.xlim(min(optics.secs_mic), max(optics.secs_mic))
    sp += 1

    pl.subplot(tsp, 1, sp, title = 'Optics Bench Accelerometer')
    pl.plot(optics.secs_accel, optics.accel, label = 'optics')
    pl.xlim(min(optics.secs_accel), max(optics.secs_accel))
    sp += 1

    pl.subplot(tsp, 1, sp, title = 'Optics Bench Position')
    pl.plot(time, optics1, label = 'Optics 1')
    pl.plot(time, optics2, label = 'Optics 2')
    pl.plot(time, optics3, label = 'Optics 3')
    pl.legend()
    sp += 1

    pl.tight_layout()
    # fig.autofmt_xdate()
    if save:
        pl.savefig(title + 'all.png')
    
    # # az and el
    # fig = pl.figure()
    # pl.subplot(211, title = 'Actual Az')
    # pl.plot(time, az)

    # pl.subplot(212, title = 'Actual El')
    # pl.plot(time, el)
    # pl.tight_layout()
    # fig.autofmt_xdate()
    # if save:
    #     pl.savefig(title + 'az-el.png')

    # # tracker errors
    # fig = pl.figure()  
    # pl.subplot(211, title = 'Az Errors')
    # pl.plot(time, azerr)
    # pl.ylim(-.05, .05)

    # pl.subplot(212, title = 'El Errors')
    # pl.plot(time, elerr)
    # pl.ylim(-.06, .06)
    # pl.tight_layout()
    # fig.autofmt_xdate()
    # if save:
    #     pl.savefig(title + 'tracker-errors.png')

    # # az and el rates
    # fig = pl.figure()
    # pl.subplot(211, title = 'Az rate')
    # pl.plot(time, azrate)

    # pl.subplot(212, title = 'El rate')
    # pl.plot(time, elrate)
    # pl.tight_layout()
    # fig.autofmt_xdate()
    # if save:
    #     pl.savefig(title + 'az-el-rate.png')
    
    if not save:
        pl.show()

    pl.close('all')

def acc_corr_plots(start, end, fig, save = False):
    i = 0
    while i < len(dat_start) - 1:
        if dat_start[i] <= start and start < dat_start[i + 1]:
            if dat_start[i + 1] < end:
                raise RuntimeError("Sorry, we can't bridge good " + 
                                   "vibes data files.\n" + 
                                   "%s is between %s and %s" 
                                   %(dat_start[i + 1].astimezone(sptz),
                                     start.astimezone(sptz), 
                                     end.astimezone(sptz)))
            gvdat = GoodVibeReader(dat_start[i].strftime('%Y%m%d_%H%M%S'), 
                                   verbose = False)
            break
        if i == len(dat_start) - 2:
            raise RuntimeError("Sorry, we don't have data from %s yet" 
                               %str(start.astimezone(sptz)))
        i += 1
        
    rxx = gvdat.rxx.get_section(start, end)
    rxy = gvdat.rxy.get_section(start, end)
    optics = gvdat.optics.get_section(start, end)
    all_gv = [rxx, rxy, optics]
    data = SPTDataReader(experiment = 'SPTpol', verbose = False, quiet = True,
                         master_configfile='sptpol_stripped_master_config')
    data.readData(start.astimezone(UTC), end.astimezone(UTC), 
                  verbose = False, quiet = True, 
                  process_psds = False, remove_unknown_bolos=False, 
                  correct_global_pointing = False)

    for b in all_gv:
        b.make_time()
        b.secs_mic = b.mic_t
        b.secs_accel = b.accel_t

    # prep data
    time = data.antenna.track_utc
    elenc1 = data.antenna.track_rawenc[0]
    elenc2 = data.antenna.track_rawenc[1]
    azerr = data.antenna.track_err[0]
    elerr = data.antenna.track_err[1]
    az = data.antenna.track_actual[0]
    el = data.antenna.track_actual[1]
    azrate = data.antenna.track_act_rate[0]
    elrate = data.antenna.track_act_rate[1]
    optics1 = data.antenna.scu_benchact[0]
    optics2 = data.antenna.scu_benchact[1]
    optics3 = data.antenna.scu_benchact[2]

    dt = np.diff(time)
    dt = map(timedelta.total_seconds, dt)
    azacc = np.diff(azrate) / dt
    elacc = np.diff(elrate) / dt

    len_dec = 50
    n_dec = int(np.ceil(float(len(azacc)) / len_dec))
    azacc_dec = np.empty(n_dec)
    elacc_dec = np.empty(n_dec)
    
    len_dec_accel = float(len(rxx.accel)) / n_dec
    x_accel_dec = np.empty(n_dec)
    y_accel_dec = np.empty(n_dec)
    optics_accel_dec = np.empty(n_dec)
    for i in range(n_dec - 1):
        azacc_dec[i] = np.mean(azacc[i * len_dec:(i + 1) * len_dec])
        elacc_dec[i] = np.mean(elacc[i * len_dec:(i + 1) * len_dec])
        x_accel_dec[i] = np.mean(rxx.accel[i * len_dec:
                                               (i + 1) * len_dec_accel])
        y_accel_dec[i] = np.mean(rxy.accel[i * len_dec:
                                               (i + 1) * len_dec_accel])
        optics_accel_dec[i] = np.mean(optics.accel[i * len_dec:
                                                   (i + 1) * len_dec_accel])

    azacc_dec[n_dec - 1] = np.mean(azacc[(n_dec - 1) * len_dec:])
    elacc_dec[n_dec - 1] = np.mean(elacc[(n_dec - 1) * len_dec:])    

    x_accel_dec[i] = np.mean(rxx.accel[(n_dec - 1) * len_dec_accel:])
    y_accel_dec[i] = np.mean(rxy.accel[(n_dec - 1) * len_dec_accel:])
    optics_accel_dec[i] = np.mean(optics.accel[(n_dec - 1) * len_dec_accel:])

    x_accel_dec -= np.mean(x_accel_dec)
    y_accel_dec -= np.mean(y_accel_dec)
    optics_accel_dec -= np.mean(optics_accel_dec)
    
    azacc = azacc_dec
    elacc = elacc_dec
    acc_inds = range(0, len(time), len_dec)

    accel_inds = range(0, len(rxx.accel), len_dec)
    
    pl.figure(fig.number)
    pl.subplot(321)
    pl.plot(azacc, x_accel_dec, 'b,')
    pl.ylabel('X Accelerometer')
    pl.subplot(322)
    pl.plot(elacc, x_accel_dec, 'b,')

    pl.subplot(323)
    pl.plot(azacc, y_accel_dec, 'b,')
    pl.ylabel('Y Accelerometer')
    pl.subplot(324)
    pl.plot(elacc, y_accel_dec, 'b,')

    pl.subplot(325)
    pl.plot(azacc, optics_accel_dec, 'b,')
    pl.ylabel('Optics Accel')
    pl.xlabel('Az Acceleration')
    pl.subplot(326)
    pl.plot(elacc, optics_accel_dec, 'b,')
    pl.xlabel('El Acceleration')

    return fig

def plot_accel_glitches():
    f = open('accel_glitches.pkl')
    times = pickle.load(f)
    f.close()
    dt = timedelta(minutes = 10)
    
    for t in times[:30]:
        start = sptz.localize(t - dt)
        end = sptz.localize(t + dt)
        savename = t.strftime('glitch_plots/accel/%Y%m%d_%H%M%S/')
        try:
            os.mkdir(savename)
        except OSError:
            pass
        try:
            mk_plot(start.astimezone(sptz), end.astimezone(sptz), 
                    savename, save = True)
        except RuntimeError, err:
            print '%s failed because:\n%s' %(t, err)

def make_scatter():
    f = open('accel_glitches.pkl')
    times = pickle.load(f)
    f.close()
    dt = timedelta(minutes = 10)
    
    fig = pl.figure()
    which_times = pl.random_integers(0, len(times) - 1, 5)
    
    for i in which_times:
        t = times[i]
        start = sptz.localize(t - dt)
        end = sptz.localize(t + dt)
        try:
            fig = acc_corr_plots(start, end, fig)
        except RuntimeError, err:
            print 'Fail! ' + str(err)

    pl.figure(fig.number)
    pl.tight_layout()
    pl.savefig('/home/ndhuang/analysis/goodvibes/glitch_plots/acc_scatter.png')

def mic_psd(start, end, title, save):
    i = 0
    while i < len(dat_start) - 1:
        if dat_start[i] <= start and start < dat_start[i + 1]:
            if dat_start[i + 1] < end:
                raise RuntimeError("Sorry, we can't bridge good " + 
                                   "vibes data files.\n" + 
                                   "%s is between %s and %s" 
                                   %(dat_start[i + 1].astimezone(sptz),
                                     start.astimezone(sptz), 
                                     end.astimezone(sptz)))
            gvdat = GoodVibeReader(dat_start[i].strftime('%Y%m%d_%H%M%S'), 
                                   verbose = False)
            break
        if i == len(dat_start) - 2:
            raise RuntimeError("Sorry, we don't have data from %s yet" 
                               %str(start.astimezone(sptz)))
        i += 1
        
    rxx = gvdat.rxx.get_section(start, end)
    rxy = gvdat.rxy.get_section(start, end)
    optics = gvdat.optics.get_section(start, end)
    all_gv = [rxx, rxy, optics]

    # xmic = bin_func(rxx.mic, max, n = 50)
    # xtime = bin_func(rxx.secs_mic, np.mean, n = 50)
    xmic = rxx.mic * rxx.mic
    xtime = rxx.secs_mic
    xpxx, xfreq = pl.mlab.psd(xmic, Fs = float(len(xmic)) / xtime[-1],
                              NFFT = nextpow2(len(xmic)) / 2)

    # ymic = bin_func(rxy.mic, max, n = 50)
    # ytime = bin_func(rxy.secs_mic, np.mean, n = 50)
    ymic = rxy.mic * rxy.mic
    ytime = rxy.secs_mic
    ypxx, yfreq = pl.mlab.psd(ymic, Fs = float(len(ymic)) / ytime[-1],
                              NFFT = nextpow2(len(ymic)) / 2)

    # opticsmic = bin_func(optics.mic, max, n = 50)
    # opticstime = bin_func(optics.secs_mic, np.mean, n = 50)
    opticsmic = optics.mic * optics.mic
    opticstime = optics.secs_mic
    opticspxx, opticsfreq = pl.mlab.psd(opticsmic, 
                                        Fs = float(len(opticsmic) / 
                                                   opticstime[-1]),
                                        NFFT = nextpow2(len(opticsmic)) / 2)
    
    fig = pl.figure()
    pl.subplot(311, title = 'X mic')
    pl.semilogy(xfreq, xpxx)
    pl.ylim(1e-1, 1e5)
    pl.subplot(312, title = 'Y mic')
    pl.semilogy(yfreq, ypxx)
    pl.ylim(1e-1, 1e5)
    pl.ylabel('Mic Signal^2 / Hz')
    pl.subplot(313, title = 'Optics mic')
    pl.semilogy(opticsfreq, opticspxx)
    pl.ylim(1e-1, 1e5)
    pl.xlabel('Frequency (Hz)')
    pl.tight_layout()
    if save:
        pl.savefig(title + 'psd_full.png')

    pl.subplot(311, title = 'X mic')
    pl.xlim(0, 3.5)
    pl.ylim(1e-1, 1e5)
    pl.subplot(312, title = 'Y mic')
    pl.xlim(0, 3.5)
    pl.ylim(1e-1, 1e5)
    pl.ylabel('Mic Signal^2 / Hz')
    pl.subplot(313, title = 'Optics mic')
    pl.xlim(0, 3.5)
    pl.ylim(1e-1, 1e5)
    pl.xlabel('Frequency (Hz)')
    pl.tight_layout()
    if save:
        pl.savefig(title + 'psd_zoom.png')

    # find the PT peaks and plot them
    xinds = np.nonzero(np.bitwise_and(xfreq > 1.4, xfreq < 1.45))[0]
    xlow_peak = np.nonzero(xpxx[xinds] == max(xpxx[xinds]))[0][0]
    xlow_peak = xfreq[xinds][xlow_peak]

    xinds = np.nonzero(np.bitwise_and(xfreq > 1.55, xfreq < 1.6))[0]
    xhigh_peak = np.nonzero(xpxx[xinds] == max(xpxx[xinds]))[0][0]
    xhigh_peak = xfreq[xinds][xhigh_peak]

    yinds = np.nonzero(np.bitwise_and(yfreq > 1.4, yfreq < 1.45))[0]
    ylow_peak = np.nonzero(ypxx[yinds] == max(ypxx[yinds]))[0][0]
    ylow_peak = yfreq[yinds][ylow_peak]

    yinds = np.nonzero(np.bitwise_and(yfreq > 1.55, yfreq < 1.6))[0]
    yhigh_peak = np.nonzero(ypxx[yinds] == max(ypxx[yinds]))[0][0]
    yhigh_peak = yfreq[yinds][yhigh_peak]

    opticsinds = np.nonzero(np.bitwise_and(opticsfreq > 1.4, 
                                          opticsfreq < 1.45))[0]
    opticslow_peak = np.nonzero(opticspxx[opticsinds] == \
                                 max(opticspxx[opticsinds]))[0][0]
    opticslow_peak = opticsfreq[opticsinds][opticslow_peak]

    opticsinds = np.nonzero(np.bitwise_and(opticsfreq > 1.55, 
                                       opticsfreq < 1.6))[0]
    opticshigh_peak = np.nonzero(opticspxx[opticsinds] == \
                                     max(opticspxx[opticsinds]))[0][0]
    opticshigh_peak = opticsfreq[opticsinds][opticshigh_peak]

    width = .005
    ax = fig.add_subplot(311, title = 'X mic')
    pl.xlim(1.4, 1.6)
    pl.ylim(1e-2, 1e5)
    pl.axvspan(xlow_peak - width, xlow_peak + width, color = 'r', alpha = .5)
    pl.axvspan(xhigh_peak - width, xhigh_peak + width, color = 'r', alpha = .5)
    ax.set_xticks([xlow_peak, xhigh_peak])
    ax = fig.add_subplot(312, title = 'Y mic')
    pl.xlim(1.4, 1.6)
    pl.ylim(1e-2, 1e5)
    pl.axvspan(ylow_peak - width, ylow_peak + width, color = 'r', alpha = .5)
    pl.axvspan(yhigh_peak - width, yhigh_peak + width, color = 'r', alpha = .5)
    ax.set_xticks([ylow_peak, yhigh_peak])
    pl.ylabel('Mic Signal^2 / Hz')
    ax = fig.add_subplot(313, title = 'Optics mic')
    pl.xlim(1.4, 1.6)
    pl.ylim(1e-2, 1e5)
    pl.axvspan(opticslow_peak - width, opticslow_peak + width, 
            color = 'r', alpha = .5)
    pl.axvspan(opticshigh_peak - width, opticshigh_peak + width, 
            color = 'r', alpha = .5)
    ax.set_xticks([opticslow_peak, opticshigh_peak])
    pl.xlabel('Frequency (Hz)')
    pl.tight_layout()
    if save:
        pl.savefig(title + 'psd_super_zoom.png')

    ax = fig.add_subplot(311, title = 'X mic')
    ax.set_yscale('linear')
    pl.ylim(0, 15000)
    ax = fig.add_subplot(312, title = 'Y mic')
    ax.set_yscale('linear')
    pl.ylim(0, 15000)
    ax = fig.add_subplot(313, title = 'Optics mic')
    ax.set_yscale('linear')
    pl.ylim(0, 15000)
    if save:
        pl.savefig(title + 'psd_super_zoom_linear.png')
    


if __name__ == '__main__':
    #plot_accel_glitches()
    # make_scatter()
    # sys.exit()

    accel_sections = (
        ('20121012_015603', '20121012_025603', 'cycle', 'local'),
        ('20121011_215351', '20121011_215437', 'turnaround', 'UTC'),
        ('20121012_115240', '20121012_115300', 'single-zoom', 'local')
        )

    mic_sections = (
        ('20121012_015603', '20121012_025603', 'cycle_2', 'local'),
        ('20121017_040818', '20121017_041818', 'jts_2', 'UTC'),
        ()
        )
    sections = mic_sections

    for sec in sections:
        if sec[-1] == 'UTC':
            tzinfo = UTC
        else:
            tzinfo = pytz.timezone('Antarctica/South_Pole')
        start = tzinfo.localize(datetime.strptime(sec[0], '%Y%m%d_%H%M%S'))
        end = tzinfo.localize(datetime.strptime(sec[1], '%Y%m%d_%H%M%S'))
        title = '/home/ndhuang/analysis/goodvibes/glitch_plots/' + sec[2]
        mic_psd(start.astimezone(sptz), end.astimezone(sptz), title, 
                save = True)
