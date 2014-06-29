from sptpol_software.util import files
import glob
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as pl

mapfiles = glob.glob('/data/sptdat/auxdata/map/autoprocessed_maps/ra5hdec-35/coadds/left/*150ghz.h5')
mapfiles = sorted(mapfiles)

for i, mf in enumerate(mapfiles):
    print mf
    mapp = files.read(mf)
    mapp.removeWeight()
    fig = pl.figure()
    mapp.plot('T', bw = True, vmin = -5e-4, vmax = 5e-4, figure = 1)
    dpi = fig.get_dpi()
    fig.set_size_inches((1920. / dpi, 1200. / dpi))
    fig.tight_layout()
    pl.savefig('/home/ndhuang/plots/pretty_maps/%d.png' %i)
    pl.close('all')

    
