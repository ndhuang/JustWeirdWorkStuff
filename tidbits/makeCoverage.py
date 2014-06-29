import glob
import os, sys
from sptpol_software.util import files

def coadd(mapfiles, pol = True):
    coadd = None
    for mf in mapfiles:
        if coadd is None:
            coadd = files.read(mf)
        else:
            coadd += files.read(mf)
    return coadd

def getMapFiles(mapdir, freq):
    freq = str(freq)
    maps = glob.glob(os.path.join(mapdir, 'left', '*%sghz.*' %freq))
    maps += glob.glob(os.path.join(mapdir, 'right', '*%sghz.*' %freq))    
    return maps

if __name__ == '__main__':
    mapdir = sys.argv[1]
    maps150 = getMapFiles(mapdir, 150)
    coadd150 = coadd(maps150)
    maps090 = getMapFiles(mapdir, 90)
    coadd090 = coadd(maps090)
    # files.fits.writeSptFits('150coverage.fits', map=weight150)
    # files.fits.writeSptFits('090coverage.fits', map=weight090)
    
