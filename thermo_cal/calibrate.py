import numpy as np
from numpy.polynomial import chebyshev as cheby

class CalRange(object):
    def __init__(self, lower, upper, ZL, ZU, order):
        self.lower = lower
        self.upper = upper
        self.ZL = ZL
        self.ZU = ZU
        self.order = order

thermo_types = {'RuO2': [CalRange(.05, .95,
                                 3.35453159798, 5.,
                                 8),
                        CalRange(.95, 6.5,
                                 3.08086045368, 3.44910010859,
                                 9),
                        CalRange(6.5, 40,
                                 2.95500000000, 3.10855552727,
                                 9)]}

def fit_range(R, T, calrange, redo_lims = True):
    # try binning in T to estimate noise for each point
    inds = np.where((T < calrange.upper) & (T > calrange.lower))
    Z = np.log10(R[inds])
    if redo_lims:
        ZL = np.min(Z)
        ZU = np.max(Z)
    else:
        ZL = calrange.ZL
        ZU = calrange.ZU
    x = ((Z - ZL) - (ZU - Z)) / (ZU - ZL)
    w = get_weights(x, T[inds])
    return x, cheby.chebfit(x, T[inds], calrange.order, w = w)

def get_weights(x, T):
    bins = np.linspace(np.min(T), np.max(T), 100)
    weights = np.zeros_like(x)
    for i in range(len(bins) - 1):
        inds = np.where((T >= bins[i]) & (T <= bins[i + 1]))[0]
        if len(inds) == 0:
            continue
        p = np.polyfit(T[inds], x[inds], 1)
        x_ = x[inds] - np.polyval(p, T[inds])
        std = np.std(x_)
        mean = np.mean(x_)
        sig = (x_ - mean) / std
        weights[inds] = np.fmin(1 / sig**2, np.ones_like(sig) * 1e3)
    return weights
        
