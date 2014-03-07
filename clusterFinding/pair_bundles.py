import cPickle as pickle
import IPython
import glob
from sptpol_software.util import files
import numpy as np

mask = files.read('/data39/ndhuang/clusters/ra23h30dec-55/run2/bundles1/150/mask.fits')
mask = mask.masks.apod_mask
mask = mask[348:3748, 348:3748]
bundle_dir = '/data39/ndhuang/clusters/ra23h30dec-55/run1/bundles/abbys_bundles/bundle*.fits'
# bundle_dir = 'bundles/150/bundle*.fits'
bundles = glob.glob(bundle_dir)
noise = np.zeros(50)
weight = np.zeros(50)
bundle_pairs = ['' for b in noise]
i = 0
while len(bundles) > 0:
    bf1 = bundles.pop(np.random.randint(0, len(bundles)))
    bf2 = bundles.pop(np.random.randint(0, len(bundles)))
    bundle_pairs[i] = bf1 + ', ' + bf2
    b1 = files.read(bf1)
    b2 = files.read(bf2)
    diff = (b1.map.map - b2.map.map) * mask
    good = np.nonzero(mask)
    noise[i] = np.std(diff[good])
    weight[i] = np.std((b1.weight.weight + b1.weight.weight)[good])
    print bundle_pairs[i], noise[i], weight[i]
    i += 1

f = open('bundle_pairs.pkl', 'w')
pickle.dump([bundle_pairs, noise, weight], f)
f.close()
