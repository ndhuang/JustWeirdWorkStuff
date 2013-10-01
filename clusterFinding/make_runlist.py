import os
from datetime import datetime
import numpy as np
import IPython

dat = dict(np.load('/scratch/work/mapcuts/map_cuts.npz'))
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

'''
rms: greater than 3 * med, less than .75 med
median_weight: greater than 1e8
'''

med_90rms = np.median(dat90['rms'])
med_150rms = np.median(dat150['rms'])

good90 = np.nonzero((dat90['rms'] <= 3 * med_90rms) & 
                    (dat90['rms'] >= .75 * med_90rms) & 
                    (dat90['med_w'] <= 1e8))[0]
good150 = np.nonzero((dat150['rms'] <= 3 * med_150rms) & 
                     (dat150['rms'] >= .75 * med_150rms) & 
                     (dat150 ['med_w'] <= 1e8))[0]

print 'Fraction of maps kept: %.3f' %(float(len(good150) + len(good90)) / n_maps)

f90 = open('good_90ghzmaps.txt', 'w')
for ind in good90:
    f90.write(dat90['files'][ind])
f90.close()
f150 = open('good_150ghzmaps.txt', 'w')
for ind in good150:
    f150.write(dat150['files'][ind])
f150.close()


