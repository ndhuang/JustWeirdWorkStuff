################################################################################
# FittingTools.py                                                              #
# Author: Nicholas Huang                                                       #
# Provides an easy to use interface for fitting                                #
################################################################################
import numpy as np
from scipy import optimize
import inspect, sys

class Parameter:
    """
    Helper class to provide easy fitting.  Calling the object will return
    its value.

    Parameters
    ----------
    value : number
           The parameter value
    interval : array-like, optional
              The confidence interval.  This, in general, should not be
              set by the user.

    Attributes
    ----------
    value : number
           The parameter value
    interval : array-like, optional
              The confidence interval.  This, in general, should not be
              set by the user

    """
    
    def __init__(self, value, interval = None):
        self.value = value
        self.interval = interval
        
    def set(self, value):
        '''
        set the parameter value
        '''
        self.value = value

    def setConfInt(self, interval):
        '''
        set the confidence interval

        Parameters
        ----------
        interval : array-like
                  An array-like with length 2, representing the upper and
                  lower confidence interval.
        '''
        
        self.interval = np.sort(interval)

    def getConfInt(self):
        '''
        Return the confidence interval (lower, upper).
        '''
        
        return self.interval

    def __call__(self):
        return self.value

    def __str__(self):
        if (self.interval != None):
            return '%3.6E \t(%3.6E, %3.6E)' %(self.value, self.interval[0],
                                            self.interval[1])
        return self.value.__str__()
        

def fit(function, params, y, args, rawOutput = False, weights = None,
        algorithm = None, **fitOpts):
    
    """
    Fit a function of an arbitrary number of inputs and one output

    Parameters
    ----------
    function : callable
              the function to fit.  It should NOT be a function
              of the parameters.
    params : iterable
            A list of Parameters, with their starting values set.
            The parameter values will be overwritten before each
            call to `function`.
    y : array-like
       the measured y-values
    args : array-like
       the values at which `y` was measured, as well as any other
       inputs to `function`.
    rawOutput : bool, optional
               If true, fit returns the output of the minimization
               function. Defaults to False
    weights : array-like, optional
             A vector containing the weight at each point.  If `weights`
             is None, each point is given equal weighting.  Defaults to
             None
    algorithm : string, optional
               Specifies the minimization algorithm to be used.
               Valid values are:
               * 'lm': Levenberg-Marquardt
               * 'simplex': Downhill simplex 
               * 'cg' or 'conjugate': Conjugate gradient
               * 'Powell': Powell's method
               * 'BFGS': BFGS method
               * 'newton': Newton-CG method
               * 'l-bfgs-b': L-BFGS-B constrained minimization
    **fitOpts : dict, optional
               All remaining keyword arguments are passed to the
               minimization function.  If it is not included,
               full_output = True (or the equivalent) will be
               added.
    

    Returns
    -------
    If `rawOutput` is set, this function returns the same thing as
    the minimization function used.
    Otherwise, it returns
    params : array-like
            The array of the original parameters with their updated values
    gof : dict
         A dictionary containing Goodness of Fit information:
         * 'residuals': an array of residuals (`y` - `function`(*`args`))
         * 'Reduced Chi2': the reduced Chi-squared
         * 'RMS error': The total rms errror of the fit

    Notes
    -----
    If the minimization algorithm generates a warning flag, a message
    containing warning information will be printed to standard output.

    Examples
    --------
    >>> import FittingTools as FT
    >>> x = np.array(range(5))
    >>> y = 3 * np.random.random() * x
    >>> a = FT.Parameter(2)
    >>> f = lambda x: a() * x
    >>> FT.fit(f, [a], y, x)
    >>> a()
    1.3436861316475002

    See Also
    --------
    All minimization routines come from scipy.optimize.
    """

    ##########################################################################
    # Begin error function 
    if (weights == None):
        weights = np.ones(np.shape(y))

    argList = inspect.getargspec(function)[0]
    if ('self' in argList):
        nArgs = len(argList) - 1
    else:
        nArgs = len(argList)

    if (nArgs > 1):
        # function of many variables
        def f(parameters):
            i = 0
            for p in params:
                p.set(parameters[i])
                i += 1
            return (y - function(*args)) * weights
    else:
        # function of one variable
        def f(parameters):
            i = 0
            for p in params:
                p.set(parameters[i])
                i += 1
            return (y - function(args)) * weights
    chi2 = lambda p: sum(f(p) ** 2)
    # End error function 
    ##########################################################################

    # build a list of parameter values
    p = [param() for param in params]

    # Now, run the selected minimization algorithm
    if (algorithm == None or algorithm == 'lm'):
        # Use Levenberg-Marquardt
        p, cov, infodict, mesg, flag = \
           optimize.leastsq(f, p, full_output = True, **fitOpts)
        if (rawOutput):
            return p, cov, infodict, mesg, ier
        # print warnings
        if (flag > 4):
            print mesg
        residuals = infodict['fvec'] / weights
        fMin = sum(residuals * residuals)
    else:
        if (algorithm == 'simplex'):
            p, fMin, iterations, funcCalls, flag =\
               optimize.fmin(chi2, p, full_output = True, **fitOpts)
            if (rawOutput):
                return p, fMin, iterations, funcCalls, flag
            # print warnings
            if (flag == 1):
                print 'Simplex: Warning: Maximum number of function ' +\
                      'evaluations made'
            elif(flag == 2):
                print 'Simplex: Warning: Maximum number of iterations ' +\
                      'reached.'
            
        elif (algorithm == 'cg' or algorithm == 'conjugate'):
            p, fMin, funcCalls, gradCalls, flag =\
               optimize.fmin_cg(chi2, p, full_output = True, **fitOpts)
            if (rawOutput):
                return p, fMin, funcCalls, gradCalls, flag
            # print warnings
            if (flag == 1):
                print 'Conjugate Gradient: Warning: Maximum numer of ' +\
                      'iterations reached.'
            elif (flag == 2):
                print 'Conjugate Gradient: Warning: Gradient and/or function '+\
                      'calls not changing.'

        elif (algorithm == 'powell'):
            p, fMin, direc, iterations, funcCalls, flag = \
               optimize.fmin_powell(chi2, p, full_output = True, **fitOpts)
            # print warnings
            if (rawOutput):
                return p, fMin, direc, iterations, funcCalls, flag
            if (flag == 1):
                print 'Powell: Warning: Maximum number of function ' +\
                      'evaluations reached.'
            elif(flag == 2):
                print 'Powell: Warning: Maximum number of iterations reached.'
                
        elif (algorithm == 'BFGS'):
            p, fMin, grad, Bopt, funcCalls, gradCalls, flag = \
               optimize.fmin_bfgs(chi2, p, full_output = True, **fitOpts)
            if (rawOutput):
                return p, fMin, grad, Bopt, funcCalls, gradCalls, flag
            # print warnings
            if (flag == 1):
                print 'BFGS: Warning: Maximum number of iterations reached.'
            elif (flag == 2):
                print 'BFGS: Warning: Gradient and/or function calls not ' +\
                      'changing'

        elif (algorithm == 'newton'):
            p, fMin, funcCalls, gradCalls, hessCalls, flag =\
               optimize.fmin_ncg(chi2, p, full_output == True, **fitOpts)
            if (rawOutput):
                return p, fMin, funcCalls, gradCalls, hessCalls, flag
            # print warnings
            if (flag == 1):
                print 'Newton-CG: Warning: Maximum number of iterations ' +\
                      'reached.'
                
        elif (algorithm == 'l-bfgs-b'):
            p, fMin, infodict = optimize.fmin_l_bfgs_b(chi2, p, **fitOpts)
            if (rawOutput):
                return p, fMin, infodict
            flag = infodict['warnflag']
            if (flag == 1):
                print 'L-BFGS-B: Warning: Maximum number of function ' +\
                      'evaluations reached.'
            elif (flag == 2):
                print 'L-BFGS-B: Warning: ' + infodict['task']
        else:
            print 'Algorithm unrecognized... \nExiting'
            sys.exit(1)

        residuals = f(p) / weights

    # set confidence intervals for each parameter
    # This may not work yet.  Needs verification
    #for param in params:
        #ConfInt(function, y, args, param, fMin, weights)

    chi2Reduced = fMin / (len(residuals) - len(params))
    rmsErr = np.sqrt(np.sum(residuals * residuals))

    gof = {'residuals': residuals, 'Reduced Chi2': chi2Reduced,
           'RMS error': rmsErr}
    return params, gof

def ConfInt(function, y, args, param, fMin = None, weights = None, dChi2 = 4):
    # Does this work?
    np.seterr(invalid = 'ignore', divide = 'ignore')
    if (weights == None):
        weights = np.ones(np.shape(y))
        
    argList = inspect.getargspec(function)[0]
    if ('self' in argList):
        nArgs = len(argList) - 1
    else:
        nArgs = len(argList)

    if (nArgs > 1):
        if (fMin == None):
            fMin = sum((function(*args) * weights) ** 2)
        def Chi2(paramVal):
            param.set(paramVal)
            return sum(((y - function(*args)) * weights) ** 2) - fMin - dChi2
    else:
        if (fMin == None):
            fMin = sum((function(args) * weights) ** 2)
        def Chi2(paramVal):
            param.set(paramVal)
            return sum(((y - function(args)) * weights) ** 2) - fMin - dChi2
        
    pOrig = param() # save the original value
    if (pOrig == 0):
        offset = 100
    else:
        offset = 0
    try:
        intHigh, res = optimize.brentq(Chi2, pOrig, pOrig * 11 + offset,
                                  full_output = True, maxiter = 1000)
        if (not res.converged):
            print 'ConfInt: Warning: Confidence interval did not converge'
            intHigh = np.Inf
    except ValueError:
        intHigh = np.Inf
    except RuntimeError:
        intHigh = np.Inf
        
    try:
        intLow, res = optimize.brentq(Chi2, pOrig, -9 * pOrig - offset,
                                      full_output = True, maxiter = 1000)
        if (not res.converged):
            print 'ConfInt: Warning: Confidence interval did not converge'
            intLow = -np.Inf
    except ValueError:
        intLow = -np.Inf
    except RuntimeError:
        intLow = -np.Inf

    param.set(pOrig) # restore the original value
    param.setConfInt([intLow, intHigh])
    return [intLow, intHigh]
