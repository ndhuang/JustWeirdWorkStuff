##############################################################################
# basefunctions.py                                                           #
# Author: Nicholas Huang                                                     #
# Functions for generating material properties                               #
##############################################################################
import numpy as np

def kt(T, alpha, Beta, gamma, n):
    '''
    From Jones and Runyan 2008 (arxiv: 0806.1921)
    '''
    if (not isinstance(T, np.ndarray)):
        T = np.array(T)
    return alpha * T ** (Beta + gamma * T ** n)

def NIST_cu(T, a, b, c, d, e, f, g, h, i):
    '''
    From the NIST Cryogenic Technologies Group
    '''
    if (not isinstance(T, np.ndarray)):
        T = np.array(T)
    num = a + \
          c * np.sqrt(T) +\
          e * T + \
          g * T ** 1.5 + \
          i * T * T
    denom = 1 + \
            b * np.sqrt(T) + \
            d * T + \
            f * T ** 1.5 + \
            h * T * T

    return 10 ** (num / denom)

def NIST_10(T, coeff):
    tmp = 0
    logT = np.log10(T)
    logprod = 1
    for c in coeff:
        tmp += c * logprod
        logprod *= logT
    return 10 ** tmp
