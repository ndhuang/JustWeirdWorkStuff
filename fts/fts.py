import os
import argparse
import glob
import numpy as np
from matplotlib import pyplot as pl

def load_group(files):
    ys = []
    y_errs = []
    for f in files:
        # if 'p1_open2' in f or 'p3_open2' in f:
        # if 'p1_open2' in f or 'p3_open1' in f or 'p3_open3' in f:
        #     continue
        x, y, y_err = np.loadtxt(f, unpack = True)
        ys.append(y)
        y_errs.append(y_err)
    ys = np.array(ys)
    y_errs = np.array(y_errs)
    if len(files) == 1:
        ys = ys[0]
        y_errs = y_errs[0]
        return x, ys, y_errs
    # import IPython
    # IPython.embed()
    mean = np.average(ys, weights = 1. / (y_errs**2), axis = 0)
    # std = 1. / np.sum(1. / (y_errs**2), axis = 0)
    std = np.std(ys, axis = 0)
    return x, ys, y_errs, mean, std

def single_plot(files):
    x, ys, y_errs, y, std = load_group(files)
    for y, y_err in zip(ys, y_errs):
        pl.errorbar(x, y, yerr = y_err, linestyle = '--', color = 'k')
    pl.errorbar(x, y, yerr = std, color = 'r') 
    return x, y, std

def transmission(closed_files, open_files):
    freq, y, ye, closed, closed_std = load_group(closed_files)
    freq, y, ye, open, open_std = load_group(open_files)
    trans = closed / open
    trans_std = abs(trans) * np.sqrt((closed_std / closed)**2 + 
                                     (open_std / open)**2)
    return freq, trans, trans_std
    

def make_plots(fft_files, inter_files, title = ''):
    if len(title) > 0:
        title += ' '
    pl.figure()
    pl.subplot(211)
    freq, fft_mean, fft_std = single_plot(fft_files)
    pl.title(title + 'FFT')
    pl.xlabel('Frequency (GHz)')
    pl.ylabel('Signal')

    pl.subplot(212)
    single_plot(inter_files)
    pl.yscale('log')
    ylim = pl.ylim()
    pl.ylim(2, ylim[-1])
    pl.title(title + 'Interferogram')
    pl.xlabel('Position')
    pl.ylabel('Signal')
    pl.tight_layout()
    
    pl.figure()
    pl.errorbar(freq, fft_mean, yerr = fft_std, color = 'r')
    pl.title(title + 'FFT')
    pl.xlabel('Frequency (GHz)')
    pl.ylabel('Signal')
    pl.show()

def open_check(dir, patterns):
    opens = [[] for i in patterns]
    for i, p in enumerate(patterns):
        files = glob.glob(os.path.join(dir, p + '[0-9]_fft.txt'))
        opens[i] = load_group(files)
    pl.plot(opens[0][3] / opens[1][3])
    pl.plot(opens[2][3] / opens[1][3])
    pl.plot(opens[3][3] / opens[1][3])
    pl.plot(opens[0][3] / opens[2][3])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type = str)
    parser.add_argument('pattern', type = str)
    args = parser.parse_args()
    inter_files = glob.glob(os.path.join(args.dir, args.pattern + '[0-9].txt'))
    fft_files = glob.glob(os.path.join(args.dir, args.pattern + '[0-9]_fft.txt'))
    make_plots(fft_files, inter_files)
                        
