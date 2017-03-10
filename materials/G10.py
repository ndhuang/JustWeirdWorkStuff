##############################################################################
# G10.py                                                                     #
# Author: Nicholas Huang                                                     #
# Material properties of G10                                                 #
##############################################################################
import numpy as np
from scipy import interpolate
import materials.basefunctions as bf

def cv_normal(T, verbose = True):
    '''
    Thermal conductivity in W / m K
    '''
    if (not isinstance(T, np.ndarray)):
        T = np.array(T)

    if np.any(T > 300) and verbose:
        print 'Warning: Temperature too high (valid range is .3 to 300 K)'
    if np.any(T < .3) and verbose:
        print 'Warning: Temperature too low (valid range is .3 to 300 K)'
    if np.any(T < 10) and np.any(T > 10) and vebose:
        print 'Warning: Using two different fits!  Check your results'
    lowT = np.where(T < 10)
    highT = np.where(T >= 10)
    k = np.zeros(np.shape(T))
    
    if len(lowT) > 0:
        alpha = 12.8e-3
        Beta = 2.41
        gamma = -9.21
        n = .222
        k[lowT] = bf.kt(T[lowT], alpha, Beta, gamma, n)

    if len(highT) > 0:
        coeff = [-4.1236, 13.788, -26.068, 26.272, -14.663, 4.4954, -.6905, .0397]
        k[highT] = bf.NIST_10(T[highT], coeff)
    return k

def cv_warp(T, verbose = True):
    if np.any(T > 300) and verbose:
        print 'Warning: Temperature too high (valid range is 12 to 300 K)'
    if np.any(T < 12) and verbose:
        print 'Warning: Temperature too low (valid range is 12 to 300 K)'
    coeff = [-2.64827, 8.80228, -24.8998, 41.1625, -39.8754, 23.1778, 
             -7.95635, 1.48806, -0.11701]
    return bf.NIST_10(T, coeff)
