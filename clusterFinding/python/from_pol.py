'''
grab maps, downsample, save, save T-only
'''

import os
import argparse
import numpy as np
from sptpol_software.util import files
from sptpol_software.observation.sky import Map

def dodirs(dir):
    try:
        os.makedirs(dir)
    except OSError:
        pass

def degrade_map(m, df):
    ms = np.shape(m)
    assert(ms[0] % df == 0 or ms[1]% df == 0)
    ns = list(np.shape(m))
    ns[0] /= df
    ns[1] /= df
    n = np.zeros( ns )
    for i in xrange(0,df):
        for j in xrange(0,df):
            n[:,:] += m[ i::df , j::df ]
    return n

def downsample(map, factor):
    m = degrade_map(map.map, factor)
    w = degrade_map(map.weight, factor)
    new = Map(map = m, weight = w, projection = map.projection, band = map.band, 
              polarization = map.polarization, units = map.units, reso_arcmin = map.reso_arcmin * factor,
              n_scans = map.n_scans, center = map.center, processing_applied = map.processing_applied)
    new.weighted_map = True
    return new

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('t_only_dir', type = str, default = None)
    parser.add_argument('downsampled_dir', type = str)
    parser.add_argument('maps', nargs = '+')
    parser.add_argument('--downsample-only', action = 'store_true')
    args = parser.parse_args()

    if not args.downsample_only:
        dodirs(args.t_only_dir)
    dodirs(args.downsampled_dir)

    for mf in args.maps:
        map = files.read(mf)
        if not args.downsample_only:
            tmap = map.getTOnly()
            map_name = os.path.basename(map.from_filename)
            tmap.writeToHDF5(os.path.join(args.t_only_dir, map_name), overwrite = True)
        
        if args.downsample_only:
            tmap = downsample(map, 4)
        else:
            map.degradedMap(4)
            tmap = map.getTOnly()
        map_name = os.path.basename(map.from_filename)
        tmap.writeToHDF5(os.path.join(args.downsampled_dir, map_name), overwrite = True)
