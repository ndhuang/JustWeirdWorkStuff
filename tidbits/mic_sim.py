from triang import triwave # a triangle wave generator that I wrote

from matplotlib import mlab
import numpy as np
import pylab as pl

savdir = 'mic_sim_plots/'
# generate gaussian noise with std = .1
noise = np.random.randn(10001) / 10

# generate a flat timestream with spikes
spikes = np.zeros(10001)
spikes[::100] = 1
pl.figure()
pl.subplot(211)
pl.plot(spikes)
pl.xlim(0, 600)
pl.title('Spikes')
# take the psd, with a sampling frequency of 100 Hz (so the spikes are at 1 Hz)
pxx, freq = mlab.psd(spikes, NFFT = 4096, Fs = 100, 
                     detrend = mlab.detrend_none, window = mlab.window_none,
                     noverlap = 0, pad_to = None, sides = 'default', 
                     scale_by_freq = None)
pl.subplot(212)
pl.loglog(freq, pxx)
yl = pl.ylim()
pl.vlines(1, 10e-10, 100)
pl.ylim(yl)
pl.xlim(.5, 10)
pl.title('Spikes')
pl.tight_layout()
pl.savefig(savdir + 'spikes.png')
# add noise
pl.figure()
pl.subplot(211)
spikes += noise
pl.plot(spikes)
pl.xlim(0, 600)
pl.title('Spikes + noise')
pxx, freq = mlab.psd(spikes, NFFT = 4096, Fs = 100, 
                     detrend = mlab.detrend_none, window = mlab.window_none,
                     noverlap = 0, pad_to = None, sides = 'default', 
                     scale_by_freq = None)
pl.subplot(212)
pl.loglog(freq, pxx)
yl = pl.ylim()
pl.vlines(1, 10e-10, 100)
pl.ylim(yl)
pl.xlim(.5, 10)
pl.title('Spikes + noise')
pl.tight_layout()
pl.savefig(savdir + 'spikes_noise.png')


# generate a triangular wave
tri = triwave(1, 100, 10001)
pl.figure()
pl.subplot(211)
pl.plot(tri)
pl.xlim(0, 600)
pl.title('Triangular wave')
# psd, s.t. the wave is at 1 Hz
pxx, freq = mlab.psd(tri, NFFT = 4096, Fs = 100, 
                     detrend = mlab.detrend_none, window = mlab.window_none,
                     noverlap = 0, pad_to = None, sides = 'default', 
                     scale_by_freq = None)
pl.subplot(212)
pl.loglog(freq, pxx)
yl = pl.ylim()
pl.vlines(1, 10e-10, 100)
pl.ylim(yl)
pl.xlim(.5, 10)
pl.title('Triangular wave')
pl.tight_layout()
pl.savefig(savdir + 'tri_wave.png')
# noise!
tri += noise
pl.figure()
pl.subplot(211)
pl.plot(tri)
pl.xlim(0, 600)
pl.title('Triangular wave + noise')
pxx, freq = mlab.psd(tri, NFFT = 4096, Fs = 100, 
                     detrend = mlab.detrend_none, window = mlab.window_none,
                     noverlap = 0, pad_to = None, sides = 'default', 
                     scale_by_freq = None)
pl.subplot(212)
pl.loglog(freq, pxx)
yl = pl.ylim()
pl.vlines(1, 10e-10, 100)
pl.ylim(yl)
pl.xlim(.5, 10)
pl.title('Triangular wave + noise')
pl.tight_layout()
pl.savefig(savdir + 'tri_wave_noise.png')


# generate noise inside a modified triangular envelope
# This is very close to the mic data
tri_env = triwave(1, 100, 10001)
inds = np.nonzero(tri_env < .1)[0]
tri_env[inds] = .1
pl.figure()
pl.subplot(211)
pl.plot(tri_env)
pl.xlim(0, 600)
pl.title('Triangular Envelope')
tri_noise = tri_env * noise
pl.subplot(212)
pl.plot(tri_noise)
pl.xlim(0, 600)
pl.title('Triangular envelope noise')
pl.tight_layout()
pl.savefig(savdir + 'tri_envelope.png')
# psd, with peaks at 1 Hz
pxx, freq = mlab.psd(tri_noise, NFFT = 4096, Fs = 100, 
                     detrend = mlab.detrend_none, window = mlab.window_none, 
                     noverlap = 0, pad_to = None, sides = 'default', 
                     scale_by_freq = None)
pl.figure()
pl.loglog(freq, pxx)
yl = pl.ylim()
pl.vlines(1, 10e-10, 100)
pl.ylim(yl)
pl.xlim(.5, 10)
pl.title('Triangular envelope noise')
pl.tight_layout()
pl.savefig(savdir + 'tri_envelope_psd.png')
