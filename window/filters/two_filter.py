import numpy as np

def T1_4(Th, Tc, L):
    if np.iterable(Th):
        Th = Th.copy()**4
        Tc = Tc.copy()**4
    else:
        Th = Th**4
        Tc = Tc**4
    return (L - 1) * (Tc + (2 - L) * Th) / (L - 3)

def T1(Th, Tc, L):
    return T1_4(Th, Tc, L)**.25

def T2_4(Th, Tc, L):
    if np.iterable(Th):
        Th = Th.copy()**4
        Tc = Tc.copy()**4
    else:
        Th = Th**4
        Tc = Tc**4
    return (L - 1) * (Th + (2 - L) * Tc) / (L - 3)

def T2(Th, Tc, L):
    return T2_4(Th, Tc, L)**.25

def frac_power(Th, Tc, L):
    return (T2_4(Th, Tc, L) + 
            L * T1_4(Th, Tc, L) + 
            L**2 * Th**4 - 
            Tc**4) / (Th**4)
