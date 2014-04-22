import os, glob
import numpy as np
from matplotlib import pyplot as pl
from sptpol_software.util import files

mapfiles = glob.glob('/mnt/rbfa/ndhuang/fast_500d_map/proj1/*.h5')
for mf in mapfiles:
    m = files.read(mf)
    m = m.getTOnly()
    ra = np.linspace(m.center[0] - (float(m.shape[1]) * m.reso_arcmin / 120),
                     m.center[0] + (float(m.shape[1]) * m.reso_arcmin / 120),
                     m.shape[1])
    az_w = np.sum(m.weight, 0)
    pl.figure()
    pl.plot(ra, az_w)
    pl.title('Az Weight')
    pl.ylabel('Weight')
    pl.xlabel('RA (degrees)')
    name = os.path.basename(mf).strip('.h5')
    pl.savefig('/mnt/rbfa/ndhuang/fast_500d_map/proj1/az_weight/%s.png' %name)
    pl.close('all')
