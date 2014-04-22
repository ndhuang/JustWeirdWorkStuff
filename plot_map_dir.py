import glob, sys
from os import path
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as pl
from sptpol_software.util import files

if __name__ == '__main__':
    map_dir = sys.argv[1]
    plot_dir = sys.argv[2]
    # band = sys.argv[3]
    mapfiles = glob.glob(path.join(map_dir, '*.h5'))
    for mf in mapfiles:
        m = files.read(mf)
        m.removeWeight()
        f = pl.figure()
        m.plot('T', bw = True, vmin = -1e-3, vmax = 1e-3, figure = 1)
#        m.plot('T', bw = True, weight = True, figure = 1)
        name = '.'.join(path.basename(mf).split('.')[:-1])
        f.set_size_inches(18, 12.15)
        pl.savefig(path.join(plot_dir, name + '.png'))
        pl.close('all')
