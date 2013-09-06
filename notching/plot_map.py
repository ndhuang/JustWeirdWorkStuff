# plot a map with ringing in it
import glob, os
import numpy as np
from sptpol_software.util import files

directory = '/data22/acrites/coadds_cuts_test/test11_20130503/'
mapfiles = glob.glob(os.path.join(directory, 'smap*.h5'))
m = files.read(mapfiles[0])
weight_map = m.getTOnly().weight
tcoadd_map = m.getTOnly().map
for mf in mapfiles[1:]:
    m = files.read(mf)
    t_map = m.getTOnly()
    tcoadd_map += t_map.map
    weight_map += t_map.weight

inds = np.nonzero(weight_map)
tcoadd_map[inds] /= weight_map[inds]
inds = np.nonzero(weight_map == 0)
tcoadd_map[inds] = 0
np.save('ringy_coadd', tcoadd_map)
np.save('ringy_weight', weight_map)
