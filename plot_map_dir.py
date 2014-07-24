import argparse
import glob, sys
from os import path
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as pl
from sptpol_software.util import files

def plot(mapfile, plot_dir):
    m = files.read(mapfile)
    m.removeWeight()
    f = pl.figure()
    m.plot('T', bw = True, vmin = -1e-3, vmax = 1e-3, figure = 1)
    # m.plot('T', bw = True, weight = True, figure = 1)
    name = '.'.join(path.basename(mapfile).split('.')[:-1])
    # f.set_size_inches(18, 12.15)
    pl.savefig(path.join(plot_dir, name + '.png'))
    pl.close('all')

def plotCmap(mapfile, plot_dir):
    m = files.read(mapfile)
    f = pl.figure()
    pl.imshow(m.Map.real_map_T, vmin = -1e-3, vmax = 1e-3, 
              cmap = matplotlib.cm.gray)
    pl.colorbar()
    name = '.'.join(path.basename(mapfile).split('.')[:-1])
    pl.savefig(path.join(plot_dir, name + '.png'))
    pl.close('all')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('map_dir', type = str)
    parser.add_argument('plot_dir', type = str)
    parser.add_argument('--band', type = int, default = None)
    parser.add_argument('--cmap', action = 'store_true')
    args = parser.parse_args()
    if args.band is None:
        args.band = [90, 150]
    else:
        args.band = [args.band]
    if args.cmap:
        plotfn = plotCmap
    else:
        plotfn = plot
    for band in args.band:
        band_name = '{:03d}ghz'.format(band)
        mapfiles = glob.glob(path.join(args.map_dir, '*%s.h5' %band_name))
        for mf in mapfiles:
            plotfn(mf, args.plot_dir)
