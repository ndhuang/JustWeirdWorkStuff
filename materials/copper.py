##############################################################################
# copper.py                                                                  #
# Author: Nicholas Huang                                                     #
# Material properties of copper                                              #
##############################################################################
import numpy as np
from scipy import interpolate
import basefunctions as bf

def cv_fit(Wc):
    T = np.linspace(5, 300, 500)
    out = 0
    for rrr in [50, 100, 150, 300, 500]:
        k = cv(T, rrr)
        res = cv_approx(T, rrr, Wc) - k
        out += np.sum(res**2)
    return out
    

def cv_approx(T, rrr, Wc, verbose = True):
    '''
    An approximation to the thermal conductivity in W / m K
    From NIST mongraph 177 (http://ncsx.pppl.gov/NCSX_Engineering/Materials/CopperProperties/PB92172766.pdf)
    '''
    raise NotImplementedError("Fix me?")
    # rrr-dependence
    Beta = .634 / rrr
    # parameters, 1-indexed to match the NIST equations
    P = [None, 1.754e-8, 2.763, 1102, -.165, 70, 1.756, 
         .838 / (Beta / 3e-4)**.1661]
    W0 = Beta / T
    W1 = P[1] * T**P[2] / (1 + P[1] * P[3] * T**(P[2] + P[4]) * 
                           np.exp(-(P[5] / T)**P[6])) + Wc
    W2 = P[7] * W1 * W0 / (W1 + W0)
    return 1 / (W0 + W1 + W2)

def cv(T, rrr = 100, verbose = True):
    '''
    Thermal conductivity in W / m K
    '''
    if (not isinstance(T, np.ndarray)):
        T = np.array(T)
        
    rrrs = [50, 100, 150, 300, 500]
    if (np.any(T > 300)):
        print 'Warning: Temperature too high (valid range is below 300 K)'
    a = np.zeros((9, 5))
    try:
        k_all = np.zeros((len(T), 5))
    except TypeError:
        k_all = np.zeros((1, 5))
    a[:, 0] = np.array([1.87430000e+00, -4.15380000e-01, -6.01800000e-01,
                        1.32940000e-01, 2.64260000e-01, -2.19000000e-02,
                        -5.12760000e-02, 1.48710000e-03, 3.72300000e-03])
    a[:, 1] = np.array([2.21540000e+00, -4.74610000e-01, -8.80680000e-01,
                        1.38710000e-01, 2.95050000e-01, -2.04300000e-02,
                        -4.83100000e-02, 1.28100000e-03, 3.20700000e-03])
    a[:, 2] = np.array([2.37970000e+00, -4.91800000e-01, -9.86150000e-01,
                        1.39420000e-01, 3.04750000e-01, -1.97130000e-02,
                        -4.68970000e-02, 1.19690000e-03, 2.99880000e-03])
    a[:, 3] = np.array([1.35700000e+00, 3.98100000e-01, 2.66900000e+00,
                        -1.34600000e-01, -6.68300000e-01, 1.34200000e-02,
                        5.77300000e-02, 2.14700000e-04, 0.00000000e+00])
    a[:, 4] = np.array([2.80750000e+00, -5.40740000e-01, -1.27770000e+00,
                        1.53620000e-01, 3.64440000e-01, -2.10500000e-02,
                        -5.17270000e-02, 1.22260000e-03, 3.09640000e-03])
    
    for i in range(len(a[0])):
        # generate conductivity for each purity level
        k_all[:, i] = bf.NIST_cu(T, *a[:, i])

    # now, interpolate to desired purity
    # if we are out of range, just linearly extrapolate, with the usual caveats
    k = np.zeros(len(T))
    if rrr < min(rrrs) or rrr > max(rrrs):
        if verbose:
            print "Warning: rrr out of range"
        for i in range(len(k)):
            p = np.polyfit(rrrs, k_all[i], 1)
            k[i] = np.polyval(p, rrr)
    else:
        for i in range(len(k)):
            k[i] = np.interp(rrr, rrrs, k_all[i])

    # extrapolate linearly to lower temperatures
    # Wiedemann-Franz
    Tpiv = 4.2
    ind = np.where(T < Tpiv)[0]
    if len(ind) > 0:
        kpiv = cv(Tpiv, rrr)
        k[ind] = kpiv * T[ind] / Tpiv

    return k

def c(T):
    '''
    heat capacity in J/g/K
    '''
    
    if (not isinstance(T, np.ndarray)):
        T = np.array(T)
        
    if (np.any(T > 300)):
        print 'Warning: Temperature too high (valid range is 4.2 to 300 K)'
    if (np.any(T < 4.2)):
        print 'Warning: Temperature too low (valid range is 4.2 to 300 K)'

    coeff = np.array([-1.91844, -0.15973, 8.61013, -18.996,
                      21.9661, -12.7328, 3.54322, -0.3797])

    return bf.NIST_10(T, coeff) / 1000
