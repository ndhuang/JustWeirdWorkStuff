import numpy as np
import pylab as pl
from os import path

data_dir = path.abspath('/data/ndhuang/cryodump/scan')

UC_head = np.fromfile(path.join(data_dir, 'current_rms_00.dat'))
UC_stage = np.fromfile(path.join(data_dir, 'current_rms_11.dat'))

freq = 39
fig = pl.figure()
pl.subplot(211, title = 'UC head: scan')
head_spect = np.real(np.fft.rfft(UC_head))
head_freqs = np.fft.fftfreq(head_spect.size, d = 1.0 / freq)
ind = np.argwhere([s > 0 and f > 0 for (f, s) in zip(head_freqs, head_spect)])
pl.loglog(head_freqs[ind], head_spect[ind])

pl.subplot(212, title = 'UC stage: scan')
stage_spect = np.real(np.fft.rfft(UC_stage))
stage_freqs = np.fft.fftfreq(stage_spect.size, d = 1.0 / freq)
ind = np.argwhere([s > 0 and f > 0 for (f, s) in zip(stage_freqs, stage_spect)])
pl.loglog(stage_freqs[ind], stage_spect[ind])
pl.savefig('scan.png')

pl.show()
