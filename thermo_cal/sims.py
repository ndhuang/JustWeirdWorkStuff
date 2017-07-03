import numpy as np
from numpy.polynomial import chebyshev


def undo_cal(T, cal_R, cal_T):
    noise_T = .025 * np.random.randn(len(T))
    return np.interp(T + noise_T, cal_T, cal_R)

def load_cal(calfile):
    T, R = np.loadtxt(calfile, usecols = [0, 1], unpack = True,
                      converters = {1: lambda s: float(s.replace('D', 'E'))})
    return R, T

def load_data(datafile = '/home/ndhuang/SPT/cut_temps.txt'):
    return np.loadtxt(datafile, usecols = [1], delimiter = ';')

