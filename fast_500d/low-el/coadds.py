import os, glob
from sptpol_software.util import files

def coadd(directory, band):
    mapfiles = glob.glob(os.path.join(directory, '*%sghz.h5' %band))
    coadd = None
    for mf in mapfiles:
        _map = files.read(mf)
        if coadd is None:
            coadd = _map
        else:
            coadd += _map
    return coadd

def coverage(band):
    return coadd('/mnt/rbfa/ndhuang/fast_500d_map/proj1/', band)

def noise(band):
    return coadd('/mnt/rbfa/ndhuang/fast_500d_map/run3/map_ra0hec-57.5/ra0hdec-57.5/coadds/', band)

def noise_diff(band):
    directory = '/mnt/rbfa/ndhuang/fast_500d_map/run3/map_ra0hec-57.5/ra0hdec-57.5/coadds/'
    mapfiles = glob.glob(os.path.join(directory, '*%sghz.h5' %band))
    # ensure an even number of maps
    if len(mapfiles) %2 != 0:
        mapfiles = mapfiles[1:]
    coadd = None
    for i, mf in enumerate(mapfiles):
        _map = files.read(mf)
        if coadd is None:
            coadd = _map
        else:
            try:
                if i %2 == 0:
                    coadd += _map
                else:
                    coadd -= _map
            except ValueError:
                print mf
                pass
    return coadd

