import os, sys
import cPickle as pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as pl
from sptpol_software.data.readout import SPTDataReader
import scanStacker as ss

def plotStack(stacks, t, title = None):
    mean = np.mean(stacks, 1)
    std = np.std(stacks, 1)
    fig = pl.figure()
    pl.subplot(211)
    pl.plot(t, mean)
    if title is not None:
        pl.title(title + ': El')
    else:
        pl.title('El')
    pl.ylabel('Elevation (degreees)')
    pl.subplot(212)
    pl.plot(t, std * 3600)
    if title is not None:
        pl.title(title + ': Std of Stack')
    else:
        pl.title('Std of Stack')
    pl.ylabel('Std (arcmin$^2$)')
    return fig

if __name__ == '__main__':
    num_scans = 5
    names = {0: 'Normal', 1: '10% Reduction', 
             2: '20% Reduction', 3: '30% Reduction'}
    plot_dir = '/home/ndhuang/plots/scan_profiles/stacks/'
    plot_fmt = 'eps'
    f = open('/home/ndhuang/spt_code/sptpol_software/scratch/ndhuang/scan_maker/el_tests_by_scan.pkl', 'r')
    times = pickle.load(f)
    f.close()
    
    start = '140504 13:36:38'
    stop = '140504 17:01:57'
    null = open('/dev/null', 'w')
    data = [SPTDataReader(start, stop, quiet = True, 
                          master_configfile='sptpol_stripped_master_config')
            for i in range(4)]
    # data = SPTDataReader(start, stop, quiet = True,                          
    #                      master_configfile='sptpol_stripped_master_config')  
    skip = False
    for scan in times:
        print '==============================%s====================' %scan
        # method verification
        # start = times[scan][0][0]
        # stop  = times[scan][0][1]
        # data.readData(start, stop, standardize_samplerates = False, 
        #               correct_global_pointing = False)
        # el = data.antenna.track_actual[1]
        # el_err = data.antenna.track_err[1]
        # el_stacks, n = ss.stack(el, num_scans)
        # time = np.arange(n) * .01
        # fig = plotStack(el_stacks, time, title = scan)
        # pl.savefig('/home/ndhuang/plots/scan_profiles/stacks/%s_pos.png' %scan)
        # pl.close(fig)
        # err_stacks = ss.makeStacks(el_err, num_scans, n)
        # fig = plotStack(err_stacks, time, title = scan + ' err')
        # pl.savefig('/home/ndhuang/plots/scan_profiles/stacks/%s_err.png' %scan)
        # pl.close(fig)
        el = []
        el_err = []
        i = 0
        while i < len(times[scan]):
            start = times[scan][i][0]
            stop  = times[scan][i][1]
            data[i].readData(start, stop, standardize_samplerates = False, 
                          correct_global_pointing = False)
            try:
                el_tmp, n = ss.stack(data[i].antenna.track_actual[1], 
                                     num_scans)
            except RuntimeError, err:
                sys.stderr.write("Caught an error for %s: %s\n" %(scan, err))
                i = len(times[scan]) # hack- we want to skip this entire scan,
                                     # not just this instance of it
                skip = True
                continue
            err_tmp = ss.makeStacks(data[i].antenna.track_err[1], num_scans, n)
            el.append(np.mean(el_tmp, 1))
            el[i] -= el[i][0]
            el_err.append(np.mean(err_tmp, 1))
            i += 1
            
        if skip:
            skip = False
            continue

        # align the scans
        el, cuts = ss.alignScans(el)
        el_err = ss.makeCuts(el_err, cuts)
        # import IPython
        # IPython.embed()
        
        pl.close('all')
        pos_fig = pl.figure()
        for i, d in enumerate(data):
            time = np.arange(n) * .01
            # plot the position of each scan
            sp = pos_fig.add_subplot(211)
            sp.plot(time, el[i], label = names[i])
            # plot differences in the second subplot
            if i != 0:
                sp = pos_fig.add_subplot(212)
                sp.plot(time, el[0] - el[i], label = names[i])
        sp = pos_fig.add_subplot(211)
        pl.title('%s: El' %scan)
        print sp.title
        pl.ylabel('El (degrees)')
        sp.legend(loc = 'best')
        sp = pos_fig.add_subplot(212)
        pl.title('%s: Differential El' %scan)
        pl.ylabel('$\Delta$ El (degrees)')
        sp.legend(loc = 'best')
        pos_fig.savefig(os.path.join(plot_dir, '%s_pos.%s' %(scan, plot_fmt)),
                        dpi = 300)

        pl.close('all')
        err_fig = pl.figure()
        for i, d in enumerate(data):
            # plot the error for each scan
            sp = err_fig.add_subplot(211)
            sp.plot(time, el_err[i], label = names[i])
            # plot differences in the second subplot
            if i != 0:
                sp = err_fig.add_subplot(212)
                sp.plot(time, el_err[0] - el_err[i], label = names[i])

        sp = err_fig.add_subplot(211)
        pl.title('%s: El Error' %scan)
        pl.ylabel('El (degrees)')
        sp.legend(loc = 'best')
        sp = err_fig.add_subplot(212)
        pl.title('%s: Differential El Error' %scan)
        pl.ylabel('$\Delta$ El (degrees)')
        sp.legend(loc = 'best')
        err_fig.savefig(os.path.join(plot_dir, '%s_err.%s' %(scan, plot_fmt)),
                        dpi = 300)
        pl.close('all')
    
