import numpy as np

'''
Ti_4 is the temperature of the ith filter to the 4th power ($T_i^4$)
Ti is Ti_4**.25
i = 1 is the filter closest to the window
Each takes the following inputs:
Th: the temperature of the hot side (probably 300 K)
Tc: the temperature of the WBP
L: the fractional power that leaks through the filter
'''

def T1_4(Th, Tc, L):
    if np.iterable(Th):
        Th = Th.copy()**4
        Tc = Tc.copy()**4
    else:
        Th = Th**4
        Tc = Tc**4
    return (1 - L) * (Tc + (3 - 2 * L) * Th) / (2 * (2 - L))

def T1(Th, Tc, L):
    return T1_4(Th, Tc, L)**.25

def T2_4(Th, Tc, L):
    if np.iterable(Th):
        Th = Th.copy()**4
        Tc = Tc.copy()**4
    else:
        Th = Th**4
        Tc = Tc**4
    return (1 - L) * (Tc + Th) / 2

def T2(Th, Tc, L):
    return T2_4(Th, Tc, L)**.25

def T3_4(Th, Tc, L):
    if np.iterable(Th):
        Th = Th.copy()**4
        Tc = Tc.copy()**4
    else:
        Th = Th**4
        Tc = Tc**4
    return (1 - L) * (Th + (3 - 2 * L) * Tc) / (2 * (2 - L))

def T3(Th, Tc, L):
    return T3_4(Th, Tc, L)**.25

def frac_power(Th, Tc, L):
    '''
    Calculate the total power on the WBP
    Inputs as described above.  This is usually used to fit for L:
    func_to_minimize = lambda L, power: (f2.frac_power(300., Tc_measured, L) * 
                                         power_from_300K - power)**2
    scipy.opt.minimize(func_to_minimize, .1, args = (measured_power_on_WBP,))
    '''
    return (T3_4(Th, Tc, L) + 
            L * T2_4(Th, Tc, L) + 
            L**2 * T1_4(Th, Tc, L) + 
            L**3 * Th**4 - 
            Tc**4) / Th**4
