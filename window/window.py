import urllib
from datetime import datetime
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as pl
from scipy.special import gamma
from materials import copper

##########################################################################
# Timestream fitting (exponentials)
def xexp(t, y0, t0, c, m):
    return y0 + m * t - np.exp((t0 - t) / c)

def rev_xexp(t, y0, t0, c, m):
    return y0 + m * t + np.exp((t0 - t) / c)

def exp(t, y0, t0, c):
    return y0 - np.exp((t0 - t) / c)

def rev_exp(t, y0, t0, c):
    return y0 + np.exp((t0 - t) / c)

##########################################################################
# Integrals of a few functions for fitting to thermal conductivity
def integrated_power_2_materials(args, A, B, alpha, beta):
    # This isn't really useful so far.  Kept for posterity
    '''
    Total power one would expect from integrating two different materials w/
    power law conductivity.  Material a to material b to material a again.
    T: high and low temp for the entire piece
    A, B: normalization for each material
    alpha, beta: powers for each material
    '''
    Tmin, Tmax, power = args
    Tlow = (Tmin**(alpha + 1) + power / A)**(1 / (alpha + 1))
    Thigh = (Tmax**(alpha + 1) - power / alpha)**(1 / (alpha + 1))
    return B * (Thigh**(beta + 1) - Tlow**(beta + 1))

def integrated_power_plaw(T, A, alpha, P0):
    '''
    Simple integral of a power law.
    T: [min_temp, max_temp]
    A: scaling
    alpha: power index
    P0: offset
    '''
    return P0 + A * (T[1]**(alpha + 1) - T[0]**(alpha + 1))

def integrated_power_nist(T, A, rrr, n = 100):
    '''
    Integrate the actual thermal conductivity of copper.  Uses NIST fits
    T: [min_temp, max_temp]
    A: scaling
    rrr: purity (the usual rrr)
    n: number of data points between T[0] and T[1] to integrate over
    '''
    out = np.zeros(len(T[0]))
    for i, T_ in enumerate(zip(T[0], T[1])):
        dT = np.linspace(T_[0], T_[1], n)
        out[i] = A * np.trapz(copper.cv(dT, rrr, verbose = False), dT)
    return out

def integrated_power_poisson(T, A, l, C, alpha, n = 100):
    def poisson(k, l):
         return np.exp(k * np.log(l) - l - np.log(gamma(k + 1)))
    def power(T, l, C, alpha):
        return poisson(T, l)**alpha + 420 * (1 - np.exp(-T / C))
    out = np.zeros(len(T[0]))
    for i, T_ in enumerate(zip(T[0], T[1])):
        dT = np.linspace(T_[0], T_[1], n)
        pow = power(dT, l, C, alpha)
        out[i] = A * np.trapz(pow / max(pow), dT)
    return out
    
##########################################################################

def fit_G(Tmin, Tmax, power, f = integrated_power_plaw, error = True):
    '''
    Try to fit out thermal conductivity from Delta T and power.
    INPUTS
    ------
    Tmin, array-like
        low temperatures
    Tmax, array-like
        high temperatures
    power, array-like
        power deposited, Watts
    f, callable
        The function to which we fit.  Should be one of the above
    error, bool    
        Raise an error (True), or warn (False)
    '''
    if f == integrated_power_2_materials:
        p, cov = opt.curve_fit(f, [Tmin, Tmax, power], power, maxfev = int(1e6))
        resid = power - f([Tmin, Tmax, power], *p)
    elif f == integrated_power_nist:
        def lsq_pow(x, T, power):
            return sum((f(T, x[0], x[1]) - power)**2)
        return opt.minimize(lsq_pow, x0 = (2e-0, 0), args = ([Tmin, Tmax], power), 
                            bounds = ((0, None), (-1e3, 1e3)))
        # p, cov = opt.curve_fit(f, [Tmin, Tmax], power, p0 = [.1, 50])
        # resid = power - f([Tmin, Tmax], *p)
    elif f == integrated_power_poisson:
        def lsq_pow(x, T, power):
            return sum((f(T, *x) - power)**2)
        return opt.minimize(lsq_pow, x0 = [1e3, 35, 1, .5], 
                            args = ([Tmin, Tmax], power),
                            bounds = ((0, None), (0, None), (0, None), (0, None)))
    else:
        p, cov = opt.curve_fit(f, [Tmin, Tmax], power, maxfev = int(1e5))
        resid = power - f([Tmin, Tmax], *p)
    chi2 = np.sqrt(np.sum(resid * resid))
    return p, cov, resid
    
def fit_all_G(T_pairs, power, f = integrated_power_plaw):
    '''
    Fit thermal conductivity for many thermometer pairs
    '''
    def combined_fit(p):
        A, alpha, P0 = p
        resid = []
        for T in T_pairs:
            resid += list(f(T, A, alpha, P0) - power)
        return np.array(resid)
    p, cov, infodict, mesg, ier = opt.leastsq(combined_fit, (1, 1, 1), 
                                              full_output = True)
    return p, cov, infodict['fvec']
    
            

def fit_one(t, T, f = exp, error = True):
    '''
    Fit an exponential to a temperature
    INPUTS
    ------
    t, array-like
        Time, seconds
    T, array-like
        Temperature, K
    f, callable
        The function to which we fit.
    error, bool (optional)
        Raise an error (True), or warn (False)
    '''
    t = t.copy()
    mint = np.min(t)
    t -= mint
    p, cov = opt.curve_fit(f, t, T)
    resid = T - f(t, *p)
    chi2 = np.sqrt(np.sum(resid * resid))
    if chi2 / len(T) > 5e-2:
        if error:
            raise ValueError("Bad fit! Chi2 = {:.4f}".format(chi2 / len(T)))
        else:
            print "Bad fit! Chi2 = {:.4f}".format(chi2 / len(T))
    p[1] += mint
    return p

def fit_run(breaks, t, T, return_pow = False):
    '''
    Wrapper function to fit one thermometer over an entire run
    INPUTS
    ------
    breaks, array-like
        pairs of indices indicating the times which we should fit
    t, array-like
        Time, seconds
    T, array-like
        Temperature, K
    return_pow, bool (optional)
        Return the power alongside the fitted temperatures
    '''
    lastpow = 0
    powers = np.zeros(len(breaks))
    T_asymp = np.zeros(len(breaks))
    for i, thing in enumerate(breaks):
        s = slice(*thing[0])
        power = thing[1]
        mid = (s.start + s.stop) / 2
        if np.mean(T[s.start:mid]) < np.mean(T[mid:s.stop]):
            f = exp
        else:
            f = rev_exp
        try:
            T_asymp[i] = fit_one(t[s], T[s], f, False)[0]
        except Exception, err:
            print s
            raise err
        powers[i] = power
        lastpow = power
    inds = np.argsort(powers)
    powers = powers[inds]
    T_asymp = T_asymp[inds]
    if return_pow:
        return powers, T_asymp
    return T_asymp
        
def get_poly_coefficients():
    '''
    Grab polyfits to load curves over the network
    '''
    fname, header = urllib.urlretrieve('http://kea.physics.berkeley.edu/window_data/heat_strap_fit.npz')
    p = np.load(fname)
    urllib.urlcleanup()
    return p['head'], p['strap_bot'], p['strap_top']

def get_power(temps, polys, return_all = False):
    '''
    Since we cannot actually fit the thermal conductivity of the heat strap,
    use load curves from all 3 points on the heat strap.
    INPUTS
    ------
    temps, array-like
        temperatures at each point (cold head, bottom of the strap, top of the strap)
    polys, array-like
        polynomial coefficients for the fit to each load curve (same order as temps)
        use window.get_poly_coefficients to get the fits
    return_all, bool
        return all fitted powers, rather than their average.  Will not raise
        an error if temps are incosistent with constant load.
    '''
    powers = np.zeros_like(temps)
    for i, Tp in enumerate(zip(temps, polys)):
        T, p = Tp
        powers[i] = np.polyval(p, T)
    if return_all:
        return powers
    power = np.mean(powers)
    std = np.std(powers)
    if std > 10.:
        raise RuntimeError("Temperatures are incosistent.  Best guess of power: {:.1f}".format(power))
    return power, std


##########################################################################
# Necessary information and functions to get the interesting data out of 
# each run.  runX arrays have the following format:
# [[[start_index, stop_index], power_applied], ...]

run3 = np.array([[[141500, 154500], 1.0,],
                 [[156000, 168000], 1.96,],
                 [[169300, 185900], 4.0,],
                 [[187000, 206000], 8.5,],
                 [[209600, 332000], 17.,],
                 [[337000, 362000], 14.76],
                 [[386000, 412000], 12.84],
                 [[416000, 550000], 9.96],
                 [[592500, 640000], 19.44]])

def do_run3(data_file = '/data/window/run3_20151024/cryo/temperatures.txt'):
    t, head, b1, b2, mid, top = np.genfromtxt(data_file, skip_header = 1, 
                                              usecols = [0, 1, 3, 5, 7, 9], 
                                              unpack = True)
    power, head = fit_run(run3, t, head, True)
    b1 = fit_run(run3, t, b1)
    b2 = fit_run(run3, t, b2)
    mid = fit_run(run3, t, mid)
    top = fit_run(run3, t, top)
    return power, head, b1, b2, mid, top

run8 = np.array([[[12515, 223880], 0],
                 [[344858, 353794], 14.99**2 / 25.4],
                 [[358600, 427951], 4.99**2 / 25.4],
                 [[429300, 442250], 14.14**2 / 25.4],
                 [[442600, 454277], 7.07**2 / 25.4],
                 [[454700, 515000], 11.18**2 / 25.4],
                 [[515100, 526563], 8.66**2 / 25.4],
                 [[526700, 538000], 12.25**2 / 25.4],
                 [[538200, 603871], 10.00**2 / 25.4],
                 [[604200, 619400], 13.28**2 / 25.4],
                 [[619700, 627183], 16.00**2 / 25.4],
                 [[628400, 690400], 16.61**2 / 25.4],
                 [[690500, 704000], 17.32**2 / 25.4],
                 [[704300, 712660], 18.00**2 / 25.4],
                 [[712800, 790340], 16.70**2 / 25.4],
                 [[790800, 796740], 18.86**2 / 25.4],
                 [[797300, 813100], 19.53**2 / 25.4]]) # jankity shit happened here

def do_run8(data_file = '/data/window/run8_20151231/cryo/temperatures.txt'):
    t, head, b1, b2 = np.genfromtxt(data_file, skip_header = 1, 
                                              usecols = [0, 1, 3, 5],
                                              unpack = True)
    # deltaT = fit_run(run8, t, b2 - b1)
    power, head = fit_run(run8, t, head, True)
    b1 = fit_run(run8, t, b1)
    b2 = fit_run(run8, t, b2)
    return power, head, b1, b2

run9_foam = np.array([[[569000, 590562], 0],
                      [[592000, 660000], 8.71**2 / 25.3],
                      [[660560, 698000], 11.25**2 / 25.3],
                      [[698700, 745610], 14.25**2 / 25.3],
                      [[746300, 833957], 0]])
def do_run9(data_file = '/data/window/run9_20160110/cryo/temperatures.txt'):
    t, head, b1, b2, top, bp0, bp4 = np.genfromtxt(data_file, 
                                                   skip_header = 1, 
                                                   usecols = [0, 1, 3, 5, 7, 9, 11],
                                                   unpack = True)
    power, head = fit_run(run9_foam, t, head, True)
    b1 = fit_run(run9_foam, t, b1)
    b2 = fit_run(run9_foam, t, b2)
    top = fit_run(run9_foam, t, top)
    bp0 = fit_run(run9_foam, t, bp0)
    bp4 = fit_run(run9_foam, t, bp4)
    return power, head, b1, b2, top, bp0, bp4

hdpe_run4 = np.array([[[46800, 53870], 7.2],
                      [[54000, 61200], 20],
                      [[61400, 65300], 25],
                      [[65400, 71600], 30],
                      [[71800, 79500], 35],
                      [[79700, 86500], 40],
                      [[86800, 94000], 28],
                      [[94300, 108000], 32],
                      [[108300, 131300], 37],
                      [[131500, 136000], 22],
                      [[136200, 148000], 46]])
def do_hdpe_run4(data_file = '/data/hdpe_window/run04_20160701/cryo/temperatures.txt'):
    t, head, bot, top, head4 = np.genfromtxt(data_file, 
                                             usecols = [0, 1, 5, 9, 15], 
                                             skip_header = 1, 
                                             unpack = True, 
                                             invalid_raise = False)
    power, head = fit_run(hdpe_run4, t, head, True)
    bot = fit_run(hdpe_run4, t, bot)
    top = fit_run(hdpe_run4, t, top)
    # head4 = fit_run(hdpe_run4, t, head4)
    return power, head, bot, top

##########################################################################
# Some stuff for doing live checks while the dewar is running

def live_fit(t, Temps, slic, debug = False):
    '''
    Fit each timestream in `Temps` to an exponential.  Plot and print some results.
    '''
    print datetime.fromtimestamp(t[-1])
    for T in Temps:
        mid = (slic.start + slic.stop) / 2
        if np.mean(T[slic.start:mid]) < np.mean(T[mid:slic.stop]):
            f = exp
        else:
            if debug: print 'Downgoing'
            f = rev_exp
        p = fit_one(t[slic], T[slic], error = False, f = f)
        print '{:.04f}, {:.00f}'.format(p[0], p[2])
        # print p
        pl.figure()
        pl.plot(t[slic], T[slic], '.', markersize = 1.)
        pl.plot(t[slic], f(t[slic], *p), linewidth = 2.)
        pl.show()
