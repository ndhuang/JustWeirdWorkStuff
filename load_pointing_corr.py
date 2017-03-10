##########################################################################
# Parameters in the pointing file
# mean_ddec      : mean dec offset in degrees
# mean_dra       : mean ra offset in degrees
# sigma_combined : quadrature sum of sigmas
# sigma_ddec     :
# sigma_dra      :
# ddec           : array of dec offsets
# dra            : array of ra offsets
# radec0_corr    : the measured field center
##########################################################################
import argparse
import re
import os
from datetime import datetime
import numpy as np
from sptpol_software.util import files
from sptpol_software.observation.sky import ang2Pix

def grabField(arr, field, converter = lambda x: x):
    out = [[] for obj in arr]
    for i, obj in enumerate(arr):
        out[i] = converter(obj.pointing[field])
    return np.asarray(out)

def fnameToTime(fname):
    match = re.search("(\d{8}_\d{6})_", fname)
    if match is None:
        return None
    return datetime.strptime(match.groups()[0], "%Y%m%d_%H%M%S")

def getMap(fname):
    dirname, bname = os.path.split(fname)
    mapname = bname[:-14] + '.h5'
    if dirname.endswith('maps') or 'bundle' in dirname:
        map_dir = dirname
    else:
        map_dir = os.path.join(os.path.dirname(dirname), 'maps')
    return files.read(os.path.join(map_dir, mapname))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs = '+', type = str)
    parser.add_argument('--field', type = str, default = None)
    parser.add_argument('--coadd', action = 'store_true',
                        help = "Coadd maps with good pointing")
    args = parser.parse_args()
    if args.field is not None:
        import field_centers
        radec0_nom = field_centers.centers[args.field]
    pting = [[] for f in args.files]
    times = [[] for f in args.files]
    for i, f in enumerate(args.files):
        pting[i] = files.read(f)
        times[i] = fnameToTime(f)
    times = np.asarray(times)
    mddec = grabField(pting, 'mean_ddec')
    mdra = grabField(pting, 'mean_dra')
    sddec = grabField(pting, 'sigma_ddec')
    sdra = grabField(pting, 'sigma_dra')
    radec0 = grabField(pting, 'radec0_corr')
    to_arr = lambda x: np.asarray([x]).flatten()
    dra = grabField(pting, 'dra', converter = to_arr)
    nsrc = np.asarray([len(r) for r in dra])

    if args.coadd:
        good = np.where((nsrc > 1) & (abs(sdra) < .1))[0]
        coadd = getMap(args.files[good[0]])
        y0, x0 = ang2Pix(np.transpose(radec0), coadd.center, .25, coadd.shape, 
                         return_validity = False)
        y0_nom, x0_nom = ang2Pix(coadd.center, coadd.center, .25, coadd.shape, 
                                 return_validity = False)
        coadd.map = np.roll(coadd.map, x0_nom - x0[0], axis = 1)
        coadd.weight = np.roll(coadd.weight, x0_nom - x0[0], axis = 1)
        coadd.map = np.roll(coadd.map, y0_nom - y0[0], axis = 0)
        coadd.weight = np.roll(coadd.weight, y0_nom - y0[0], axis = 0)
        for i in good[1:]:
            print args.files[i]
            print x0_nom - x0[i], y0_nom - y0[i]
            m = getMap(args.files[i])
            m.map = np.roll(m.map, x0_nom - x0[i], axis = 1)
            m.weight = np.roll(m.weight, x0_nom - x0[i], axis = 1)
            m.map = np.roll(m.map, y0_nom - y0[i], axis = 0)
            m.weight = np.roll(m.weight, y0_nom - y0[i], axis = 0)
            coadd += m
        coadd.writeToHDF5(os.path.join('/data/ndhuang/misc/', 
                                       args.field + 'pting_corr_azbundle.h5'),
                          overwrite = True)
    else:
        import IPython
        IPython.embed()
