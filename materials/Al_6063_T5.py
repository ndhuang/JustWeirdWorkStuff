##############################################################################
# cf_rod.py                                                                  #
# Author: Nicholas Huang                                                     #
# Material properties of Al 6061-T5 rod in W / m K                           #
##############################################################################
import numpy as np
from scipy import interpolate
import materials.basefunctions as bf

def cv(T):
    if (not isinstance(T, np.ndarray)):
        T = np.array(T)

    if (np.any(T > 300)):
        print 'Warning: Temperature too high (valid range is 1 to 300 K)'
    if (np.any(T < 1)):
        print 'Warning: Temperature too low (valid range is 1 to 300 K)'
    coeff = [22.401433, -141.1343, 394.95461, -601.1537, 547.83202, 
             -305.9969, 102.38656, -18.81023, 1.4576882]
    return bf.NIST_10(T, coeff)
