##############################################################################
# cf_rod.py                                                                  #
# Author: Nicholas Huang                                                     #
# Material properties of Al 6061-T6 rod in W / m K                           #
##############################################################################
import numpy as np
from scipy import interpolate
import materials.basefunctions as bf

def cv(T):
    '''
    Thermal conductivity paralell to fibers
    source: Runyan and Jones 2008 (arxiv:0806.1921)
    '''
    if (not isinstance(T, np.ndarray)):
        T = np.array(T)

    if (np.any(T > 80)):
        print 'Warning: Temperature too high (valid range is 2 to 80 K)'
    if (np.any(T < 2)):
        print 'Warning: Temperature too low (valid range is 2 to 80 K)'
    coeff = [-1.37737, -3.40668, 20.5842, -53.1244, 73.2476, -57.6546, 
             26.1192, -6.34790, 0.640331]
    if len(np.shape(T)) == 0:
        # T is a scalar
        if T > 80:
            return bf.NIST_10(80., coeff)
        else:
            return bf.NIST_10(T, coeff)
    inds = np.where(T > 80.)[0]
    val = np.zeros(np.shape(T))
    val[inds] = bf.NIST_10(80., coeff)
    val[T < 80] = bf.NIST_10(T[T < 80], coeff)
    return val

