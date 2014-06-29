import glob
import os, sys
import cPickle as pickle
import numpy as np
from sptpol_software.util import files
from sptpol_software.analysis.maps import calculateNoise

def getNoise(mapfiles, noise_ell = [5500, 6500]):
    noise = np.zeros(np.shape(mapfiles))
    for i, mf in enumerate(mapfiles):
        m = files.read(mf)
        noise[i] = calculateNoise(m.removeWeight(), ell_range = noise_ell, 
                                  return_noise = True, quiet = True)[0]
        del m
    return noise

def getMapFiles(mapdir, freq):
    freq = str(freq)
    maps = glob.glob(os.path.join(mapdir, 'left', '*%sghz.*' %freq))
    maps += glob.glob(os.path.join(mapdir, 'right', '*%sghz.*' %freq))    
    return maps

if __name__ == '__main__':
    mapdir = sys.argv[1]
    noise = {'90': [], '150': []}
    for key in noise:
        mapfiles = getMapFiles(mapdir, key)
        mapfiles = filter(lambda mf: "crash" not in mf, mapfiles)
        noise[key] = getNoise(mapfiles)
        
    f = open('noisynoise.pkl', 'w')
    pickle.dump(noise, f)
    f.close()
