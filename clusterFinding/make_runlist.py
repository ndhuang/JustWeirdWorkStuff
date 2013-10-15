import os
from datetime import datetime
import numpy as np
from matplotlib import pyplot as pl
import IPython

dat = dict(np.load('/home/ndhuang/code/clusterFinding/map_cuts.npz'))
n_maps = len(dat['rms'])
inds = np.flatnonzero(dat['rms'] != 0)
for k in dat:
    dat[k] = dat[k][inds]

times = ['a' for i in range(len(dat['files']))]
for i, f in enumerate(dat['files']):
    f = os.path.basename(f)[:15]
    times[i] = datetime.strptime(f, '%Y%m%d_%H%M%S')

dat['times'] = np.array(times)


nist = lambda f: '150ghz' in f
files150 = map(nist, dat['files'])
inds150 = np.nonzero(files150)[0]
inds90 = np.nonzero(map(lambda x: not x, files150))[0]

dat90 = {}
dat150 = {}
for k in dat:
    dat90[k] = dat[k][inds90]
    dat150[k] = dat[k][inds150]

dat[150] = dat150
dat[90] = dat90
'''
median_weight: greater than 1e8
'''

good90 = np.nonzero((dat90['med_w'] <= 1e8))[0]
good150 = np.nonzero((dat150 ['med_w'] <= 1e8))[0]
good = {}
good[90] = good90
good[150] = good150

freqs = [150, 90]
tests = ['med_w', 'rms', 'tot_w']
thresholds = np.array([1, 2, 3, -1, -2, -3])

stats = {90: {}, 150: {}}
for k1 in stats:
    for k2 in tests:
        stats[k1][k2] = {}
        stats[k1][k2]['s'] = np.std(dat[k1][k2][good[k1]])
        stats[k1][k2]['m'] = np.median(dat[k1][k2][good[k1]])

# for f in freqs:
#     for t in tests:
#         pl.figure()
#         pl.hist(dat[f][t][good[f]], bins = 30)
#         pl.vlines(stats[f][t]['m'] + thresholds * stats[f][t]['s'], 
#                   pl.ylim()[0], pl.ylim()[1])
#         pl.title(str(f) + 'ghz: ' + t)
#     pl.show()

keepers = {}
for f in freqs:
    bools = np.array([True for i in range(len(dat[f]['rms']))])
    for t in tests:
        if f == 90 and t == 'med_w': 
            thresh = 2
        else:
            thresh = 2
        bools = bools & ((dat[f][t] < (stats[f][t]['m'] + thresh * stats[f][t]['s']))
                         &
                         (dat[f][t] > (stats[f][t]['m'] - thresh * stats[f][t]['s'])))
    keepers[f] = np.nonzero(bools)[0]

print 'Fraction of maps kept: %.3f' %(float(len(keepers[150]) + len(keepers[90])) / n_maps)

# f90 = open('/data39/ndhuang/clusters/ra23h30dec-55/run2/bundles2/good_90ghzmaps.txt', 'w')
# for ind in keepers[90]:
#     f90.write(dat[90]['files'][ind] + '\n')
# f90.close()
# f150 = open('/data39/ndhuang/clusters/ra23h30dec-55/run2/bundles2/good_150ghzmaps.txt', 'w')
# for ind in keepers[150]:
#     f150.write(dat[150]['files'][ind] + '\n')
# f150.close()


