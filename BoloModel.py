##############################################################################
# BoloModel.py                                                               #
# Author: Nicholas Huang                                                     #
# Creates a model of a bolometer (with negligible electric field effect) for #
# use by PyMC.  This module also provides functions for plotting histograms  #
# of the results, and writing the resulting statistics to a file.            #
##############################################################################
import sys

from pymc import stochastic, deterministic, Normal, Uniform
import numpy as np
import matplotlib.pyplot as pl
import plot2Ddist as p2d

def make_model(VsigDat, VbiasDat, IDat, T = .3):
    '''
    Return the parameters necessary to create a PyMC model

    Extended Summary
    ----------------
    This function creates all the parameters needed to create a PyMC model
    of a NTDGe Bolometer.  To run a MCMC on the model, it must be converted
    to a pymc.MCMC object first.

    Parameters
    ----------
    VsigDat : array_like
        The recorded signal voltage in Volts
    VbiasDat : array_like
        The voltage used to bias the bolometer in Volts
    IDat : array_like
        The current used to bias the bolometer in Amps
    T : float, optional
        The lowest possible base temperature in Kelvin.  This will be used
        as the lower limit when fitting the base temperature.  The default
        is .3 K

    Returns
    -------
    Vbias : pymc.Normal
        A distribution representing the bias voltage.  At each point,
        it is a Normal centered on the given voltage.
    I : pymc.Normal
        A distribution representing the current.  At each point it is a
        normal distribution centered on the current given by IDat.
    Vcalc : pymc.deterministic
        A function that calculates the expected signal voltage given
        a choice of parameters.
    Vsig : pymc.stochastic
        A distribution representing the signal voltage.
        This distribution should be adjusted based on the noise
        characteristics of the bolometer in question.
    Delta : pymc.Uniform
        A distribution representing Delta.  This can be adjusted
        based on bolometer characterstics.
    Tbase : pymc.Uniform
        A distribution representing the temperature of the bolometer
        with no power (i.e. I = Vbias = 0) applied.  This should be
        adjusted based on experimental setup.
    Beta : pymc.Uniform
        A distribution representing Beta.  This should not be adjusted,
        unless you have strong prior knowledge.  Otherwise, it will be
        sampled from the full range of physical values.
    R0 : pymc.Uniform
        A distribution representing R0.  This can be adjusted based on
        bolometer characteristics.
    G0 : pymc.Uniform
        A distribution representing G0.  This can be adjusted based on
        bolometer characteristics.
    Q : pymc.Uniform
        A distribution representing Q, the non-electrical power applied
        to the bolometer.  This should be adjusted based on the expected
        power.

    Other Parameters
    ----------------
    T0 : float
        An arbitrary parameter to allow for easy approximations.
        It should be near the expected base temperature.

    Notes
    -----
    This model is based on the following equations:
    ..math:: G = G_0 \frac{T}{T_0}^\Beta
    ..math:: R = R_0 e^{\sqrt{\Delta / T}}
    where G is the thermal conductivity as a function of temperature, T is
    the temperature of the bolometer (not necessarily the base temperature)
    and R is the resistance across the bolometer.  Note that this disregards
    the electric field effect.

    Example
    -------
    >>> import pymc
    >>> M = make_model(Vsig, Vbias, I)
    >>> mcmc_model = pymc.MCMC(M)
    >>> M.isample(iter = 10000, burn = 1000, thin = 5)

    It is assumed that Vsig, Vbias, and I have been initialized elsewhere.
    '''
    
    Delta = Uniform('Delta', lower = 20, upper = 90)
    Beta = Uniform('Beta', lower = 1, upper = 3)
    R0 = Uniform('R0', lower = 0, upper = 1500)
    G0 = Uniform('G0', lower = 0, upper = 1000)
    Q = Uniform('Q', lower = 0, upper = 1000)
    Tbase = Uniform('Tbase', lower = .25, upper = 5)
    T0 = .300
    Vbias = Normal('Vbias', mu = VbiasDat, tau = 1 / 1e-8,
                    value = VbiasDat, observed = True)
    I = Normal('I', mu = IDat, tau = 1 / (3e-11*3e-11),
               value = IDat, observed = True)

    @deterministic(plot = False, trace = False)
    def Vcalc(Delta = Delta, Beta = Beta, R0 = R0, I = I,
              G0 = G0, Q = Q, Tbase = Tbase, T0 = T0, RL = 60e6, V = Vbias):
        P = (I * V - I * I * RL) * 1e12
        T = ((P + Q) * (Beta + 1) * T0 ** Beta) / G0 + Tbase ** (Beta + 1)
        T = T ** (1 / (Beta + 1))
        return R0 * I * np.exp(np.sqrt(Delta / T))

    @stochastic(observed = True)
    def Vsig(value = VsigDat, mu = Vcalc, spread = .0035 / 2):
        for i in range(len(value)):
            if (value[i] < mu[i]- spread or value[i] > mu[i] + spread):
                return np.log(sys.float_info.min)
        return 1 / (spread * 2)

    return locals()

def model_hist(M, lenhist = 1e5, start = 0, suffix = '', **kwargs):
    '''
    Plot and save several histograms of each parameter to
    assess convergence

    Extended Summary
    ----------------
    This function plots and saves several histograms from each parameter.
    This histograms show the progression of the distribution throughout
    the chain.  When the distribution stops changing, the parameter has
    most likely converged to its final state.

    Parameters
    ----------
    M : pymc.MCMC or pymc.database
        The Markov chain to be plotted
    lenhist : int, optional
        Each histogram will include `lenhist` more points than the
        previous histogram.  Defaults to 100,000
    start : int
        Steps in the Markov chain before `start` will not be included
        in the histogram.  Defaults to 0 (the beginning of the chain).
    **kwargs : dict
        Any extra keyword arguments are passed to plt.hist.
    '''
    
    keys = ['R0', 'G0', 'Q', 'Beta', 'Delta', 'Tbase']
    N = int(np.ceil(len(M.trace(keys[0])[:]) / lenhist))
    width = np.ceil(np.sqrt(N))
    height = np.floor(np.sqrt(N))
    if (width * height < N):
        width += 1
    for i in range(len(keys)):
        pl.figure(figsize = (4 * width, 4 * height))
        key = keys[i]
        for j in range(N):
            pl.subplot(height, width, j + 1)
            trace = M.trace(key, chain = -1)[start:start + (j + 1) * lenhist]
            pl.hist(trace, **kwargs)
            pl.title('%s-%d' %(key, j))
        pl.savefig('%s-hist%s.png' %(key, suffix))
            
def corr(M, **kwargs):
    '''
    Plot a 2D slice of the Markov chain for all possible parameter
    pairs

    Extended Summary
    ----------------
    For each pair of parameters, plot the Markov chain.  This can be
    used to diagnose degenerate parameters, as well as priors.

    Parameters
    ----------
    M : pymc.MCMC or pymc.database
        The Markov chain to be plotted
    **kwargs : dict
        Any extra keyword arguments are passed to plt.plot
    '''
    
    keys = ['R0', 'G0', 'Q', 'Beta', 'Delta', 'Tbase']
    N = len(keys) - 1
    pl.figure(figsize = (4 * N, 4 * N))
    for i in range(N):
        j = 0
        while(j <= i):
            pl.subplot(N, N, i * N + j + 1)
            pl.plot(M.trace(keys[i + 1])[:], M.trace(keys[j])[:], '.',
                    **kwargs)
            pl.title(keys[i + 1] + '-' + keys[j])
            j += 1
    pl.savefig('corr.png')

def print_stats(M, file):
    '''
    Write the results of pymc.MCMC.stats() to file in a more readable way.

    Parameters
    ----------
    M : pymc.MCMC or pymc.database
       The Markov chain to be plotted
    file : string
        The name of the file to be written.
    '''
    f = open(file, 'w')
    stats = M.stats()
    for key in stats.keys():
        f.write(key + ': \n')
        for k in stats[key].keys():
            f.write('\t%s: ' %k)
            try:
                line = '('
                for val in stats[key][k]:
                    line += val + ', '
                line.rstrip(', ')
                line += ')'
            except TypeError:
                line = str(stats[key][k])
            line += '\n'
            f.write(line)
    f.close()

def contours(M, contourKDEthin = 1):
    '''
    Plot likelihood contours for each pair of paramters
    
    Parameters
    ----------
    M : pymc.MCMC or pymc.database
        The Markov chain to be plotted
    contourKDEthin : int, optional
        Thins the samples used for estimating the gaussian kernel density.
        Defaults to 1 (no thinning).

    See Also
    --------
    plot2Ddist (https://gist.github.com/665605)
    '''
    
    keys = ['R0', 'G0', 'Q', 'Beta', 'Delta', 'Tbase']
    N = len(keys) - 1
    pl.figure(figsize = (4 * N, 4 * N))
    for i in range(N):
        j = 0
        while(j <= i):
            ax = pl.subplot(N, N, i * N + j + 1)
            p2d.plot2Ddist([M.trace(keys[i + 1])[:], M.trace(keys[j])[:]],
                           labels = [keys[i + 1], keys[j]], 
                           contourKDEthin = contourKDEthin,
                           axeslist = [ax], plotscatter = False)
            j += 1
    pl.savefig('contours.png')
