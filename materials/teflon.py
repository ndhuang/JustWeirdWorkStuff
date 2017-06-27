import numpy as np
from scipy import interpolate
import materials.basefunctions as bf

def cv(T):
    '''
    '''
    if (not isinstance(T, np.ndarray)):
        T = np.array(T)

    if (np.any(T > 300)):
        print 'Warning: Temperature too high (valid range is 4 to 300 K)'
    if (np.any(T < 4)):
        print 'Warning: Temperature too low (valid range is 4 to 300 K)'
    
    coeff = [2.7380, -30.677, 89.430, -136.99, 124.69, -69.556, 23.320, -4.3135,
             0.33829]
    return bf.NIST_10(T, coeff)
