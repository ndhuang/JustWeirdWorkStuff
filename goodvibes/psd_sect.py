from pylab import *

from gv_datareader import GoodVibeReader
import pickle

data = GoodVibeReader('20121012_015603')

for b in data.all:
    b.split_on_timing()

psds = None
for i, s in enumerate(data.rxx.mic_sects):
    pxx, freq = mlab.psd(s, Fs = 1.0 / mean(diff(data.rxx.secs_mic_sects[i])), 
                         NFFT = 1024*8)
    pxx = pxx.flatten()
    if psds is not None:
        psds += pxx
    else: 
        psds = pxx

psds /= len(data.rxx.mic_sects)

f = open('bigpsd.pkl', 'w')
pickle.dump([freq, psds], f)
f.close()

loglog(freq, psds)
show()
