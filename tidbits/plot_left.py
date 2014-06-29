import glob, sys
from os import path
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as pl
from sptpol_software.util import files

#map_dir = '/data/sptdat/auxdata/map/autoprocessed_maps/ra3hdec-25/coadds/left/'
plot_dir =  '/data/ndhuang/plots/ra3hdec-25_monitoring'
if __name__ == '__main__':
    map_dir = sys.argv[1]
    mapfiles = glob.glob(path.join(map_dir, '*.h5'))
    for mf in mapfiles:
        m = files.read(mf)
        m.removeWeight()
        f = pl.figure()
        m.plot('T', bw = True, vmin = -2e-3, vmax = 2e-3, figure = 1)
        name = path.basename(mf).split('.')[0]
        f.set_size_inches(18, 12.15)
        pl.savefig(path.join(plot_dir, name + '.png'))
        pl.close('all')
