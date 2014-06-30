import matplotlib
matplotlib.use('Agg')
import glob
from matplotlib import pyplot as pl, cm
from sptpol_software.util import files
import numpy as np
dir = '/data39/ndhuang/clusters/ra23h30dec-55/run2/bundles2/150/bundle*.fits'
mask = '/data39/ndhuang/clusters/ra23h30dec-55/run2/bundles1/150/mask.fits'
mask = files.read(mask)
mapfiles = glob.glob(dir)
fig = pl.figure()
for mf in mapfiles:
    map = files.read(mf)
    pl.imshow(map.map.map * mask.masks.apod_mask, cmap = cm.gray, vmin = -5e-4, vmax = 5e-4)
    pl.colorbar()
    pl.savefig(mf.strip('.fits') + '.png')
    fig.clf()
