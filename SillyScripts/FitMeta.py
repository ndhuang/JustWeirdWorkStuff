import sys
import os
import re
import time
import multiprocessing

import matplotlib
# set matplotlib backend in order to run headless
matplotlib.use('agg')
import pygetdata as gd
import numpy as np
import pymc

import MetaBoloModel

##############################################################################
# Helper Functions
def ExistOrMake(path):
    # If path exists, do nothing, otherwise, make the directory
    if (not os.path.exists(path)):
        os.mkdir(path)
        return False
    return True

def _Center(Vsig, Vbias, cutoff = 2):
    # center Vsig on 0 V.  Accounts for amplifier offset
    lowAve = np.average(Vsig[np.where(Vbias < -cutoff)])
    hiAve = np.average(Vsig[np.where(Vbias > cutoff)])
    offset = (lowAve + hiAve) / 2
    Vsig -= offset
    return offset
##############################################################################
    
BUFFER = 100000
PROCESSES = 3
prefix = '/home/nick/'

files = sorted(os.listdir(prefix + 'Bolometers/LJBolos/'))
data = gd.dirfile(prefix + 'Bolometers/run7_dir')
totalSamples = data.nframes * data.spf('UnixTime')
'''
prevFrame = 0
i = 0
while (i < len(files)):
    f = files[i]
    if (not re.match('B1_([0-9]{2}-?){3}(_[0-9]{2}){3}.txt', f)):
        files.remove(f)
        continue

    # extract the load curve time and date from the file name
    date = f[3:11]
    Time = f[12:20].replace('_', ':')
    t = time.strptime('%s, %s' %(date, Time), '%m-%d-%y, %X')
    t = time.mktime(t)
    
    # find the nearest time in the DAQ record
    times = data.getdata('UnixTime', gd.INT, first_frame = prevFrame,
                         num_samples = BUFFER)
    tFrame = times[0]
    j = 0
    cont = False
    while (tFrame < t):
        if (j + prevFrame > totalSamples):
            files.remove(f)
            cont = True
            break
        if (j == BUFFER):
            prevFrame += BUFFER
            j = 0
            times = data.getdata('UnixTime', gd.INT,
                                  first_frame = prevFrame,
                                  num_samples = BUFFER)
        tFrame = times[j]
        j += 1
    if (cont):
        continue
    prevFrame += j
    if (tFrame - t >= 88):
        files.remove(f)
        continue

    # find the end of the load curve
    nSamples = 1
    while (tFrame <= t + 280):
        if (j + prevFrame >= totalSamples):
            j = totalSamples - 1 - prevFrame
            tFrame = times[j]
            break
        if (j == BUFFER):
            prevFrame += j
            j = 0
            times = data.getdata('UnixTime', gd.INT,
                                  first_frame = prevFrame,
                                  num_samples = BUFFER)
        tFrame = times[j]
        j += 1
        nSamples += 1

    T = data.getdata('Insert1ThelmaStill', gd.FLOAT, first_frame = prevFrame,
                     num_samples = nSamples)
    T = T[np.where(~np.isnan(T))]
    if (len(T) == 0):
        files.remove(f)
        continue
    if (max(T) > 1):
        files.remove(f)
        continue
    prevFrame += j
    i += 1
'''
# hokay, so, now we need to load in all the load curves
files = ['B1_09-29-11_02_14_18.txt', 'B1_10-04-11_17_10_01.txt',
         'B1_10-14-11_17_10_01.txt']
N = len(files)
Vsig = np.empty((601, 3))
Vbias = np.empty((601, 3))

for (i, f) in enumerate(files):
    load_curve = np.genfromtxt(prefix + 'Bolometers/LJBolos/' + f)
    _Center(load_curve[:, 0], load_curve[:, 1])
    Vsig[:, i] = load_curve[:, 0] / 196
    Vbias[:, i] = load_curve[:, 1]
I = (Vbias - Vsig) / 60e6

M = MetaBoloModel.make_meta_model(Vsig, Vbias, I)
M = pymc.MCMC(M, db = 'pickle')
M.isample(100)
'''
p = [[] for j in range(PROCESSES)]
for i in range(int(np.ceil(len(files) / PROCESSES))):
    for j in range(PROCESSES):
        # run a few load curves at once
        k = PROCESSES * i + j
        if (k >= len(files)):
            break
        print time.strftime('%X')
        print '%d: %s at %3.3f K' %(os.getpid(), files[k], Tave[k])
        p[j] = multiprocessing.Process(target = Fit, 
                                       args = (files[k], Tave[k]))
        p[j].start()
    for j in range(PROCESSES):
        # wait for the three to finish
        if (k >= len(files)):
            break
        p[j].join()

'''
