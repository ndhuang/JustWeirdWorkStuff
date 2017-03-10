##############################################################################
# cf_rod.py                                                                  #
# Author: Nicholas Huang                                                     #
# Material properties of carbon fiber rod in W / m K                         #
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

    if (np.any(T > 4.2)):
        print 'Warning: Temperature too high (valid range is .3 to 4.2 K)'
    if (np.any(T < .3)):
        print 'Warning: Temperature too low (valid range is .3 to 4.2 K)'
    
    alpha = 8.39e-3
    Beta = 2.12
    gamma = -1.05
    n = .181
    return bf.kt(T, alpha, Beta, gamma, n)
