import os
import cPickle as pickle
import numpy as np
from sptpol_software.util import files

def readRunlist(runlist):
    runlist = open(runlist, 'r')
    mapfiles = runlist.readlines()
    i = 0
    while i < len(mapfiles):
        mapfiles[i] = mapfiles[i].strip()
        if not os.path.exists(mapfiles[i]):
            mapfiles.pop(i)
        else:
            i += 1
    return mapfiles

if __name__ == '__main__':
    mapfiles = readRunlist('/mnt/rbfa/ndhuang/maps/clusters/ra1hdec-35/150ghz_runlist.txt')
    idf_dir = '/data/ndhuang/auxdata/idf/ra1hdec-35/data/'
    T = np.zeros(len(mapfiles))
    for i, mf in enumerate(mapfiles):
        filename = os.path.basename(mf)
        idf_name = filename.replace('clustermap_', '').replace('5_2', '5_idf_2', 1)
        idf = files.read(os.path.join(idf_dir, idf_name))
        T[i] = idf.observation.temp_avg
    
    f = open('/mnt/rbfa/ndhuang/maps/clusters/ra1hdec-35/t_avg', 'w')
    pickle.dump([T, mapfiles], f)
    f.close()
