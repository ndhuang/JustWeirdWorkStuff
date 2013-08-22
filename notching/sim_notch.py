import numpy as np
import matplotlib.pyplot as pl

'''
lines and widths as found by JT's code:
[1.5366822482666016, 1.580455] [0.0077610214558918589, 0.010909999999999975]

hard coded notches:
[[1.53425, 1.53925],
 [1.575, 1.58591],
 [3.06951, 3.07436],
 [3.15424, 3.16516],
 [4.60598, 4.61083],
 [4.7341, 4.74501]]
'''

def pointSource(t, beam_width = .0311):
    return np.exp(- t*t / (2 * beam_width*beam_width))

def zeroTF(transfer_function, freq, line, width, neg_freq = True):
    inds = np.argwhere((line - width < freq) & (line + width > freq))
    transfer_function[inds] = 0
    if neg_freq:
        inds = np.argwhere((-line - width < freq) & (-line + width > freq))
        transfer_function[inds] = 0

def notchFilter(lines = [1.54, 1.58], n_harm = 9, widths = [.01, .01], 
                neg_freq = True, plot = False):
    t = np.linspace(-20, 20, num = 40*191)
    tstream = pointSource(t)
    fourier = np.fft.fft(tstream, 2**18)
    freq = np.fft.fftfreq(len(fourier), 1./191)
    trans_fn = np.ones(len(fourier))

    for l, w in zip(lines, widths):
        w /= 2
        zeroTF(trans_fn, freq, l, w, neg_freq)
        for i in np.arange(n_harm) + 2:
            l *= i
            zeroTF(trans_fn, freq, l, w, neg_freq)
           
    new_fourier = fourier * trans_fn
    new_tstream = np.real(np.fft.ifft(new_fourier))
    if plot:
        pl.figure()
        pl.plot(t, new_tstream[:len(t)] - tstream)
        pl.show()
    return t, new_tstream[:len(t)]

if __name__ == '__main__':
    current_lines = []
    current_widths = []
    hard_coded = [[1.53425, 1.53925],
                  [1.575, 1.58591],
                  [3.06951, 3.07436],
                  [3.15424, 3.16516],
                  [4.60598, 4.61083],
                  [4.7341, 4.74501]]
    for band in hard_coded:
        current_lines.append(np.mean(band))
        current_widths.append(np.diff(band))

    current_lines += [1.5366822482666016, 1.580455]
    current_widths += [0.0077610214558918589, 0.010909999999999975]

    current_kwargs = {'lines': current_lines, 'widths': current_widths,
                      'n_harm': 9, neg_freq = True}

    proposed_kwargs = {'lines': [1.535, 1.580], 'widths': [.0035, .005],
                       'n_harm': 0, 'neg_freq': True}

    t, curr = notchFilter(**current_kwargs)
    t, curr_neg = notchFilter(neg_freq = True, **current_kwargs)
    t, prop = notchFilter(**proposed_kwargs)
    tstream = pointSource(t)

    # t, noneg = notchFilter(plot = True)
    # t, wneg = notchFilter(neg_freq = True)
    # pl.figure()
    # pl.plot(t, (noneg - wneg))
    # pl.show()
    pass
