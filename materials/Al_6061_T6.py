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

    if (np.any(T > 300)):
        print 'Warning: Temperature too high (valid range is 1 to 300 K)'
    if (np.any(T < 1)):
        print 'Warning: Temperature too low (valid range is 1 to 300 K)'
    coeff = [0.07918, 1.0957, -0.07277, 0.08084, 0.02803, -0.09464, 
             0.04179, -0.00571]
    return bf.NIST_10(T, coeff)
