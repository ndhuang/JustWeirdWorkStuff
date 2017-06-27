import os
import argparse
import cPickle as pickle
import shutil
import tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pl
import scipy.optimize as opt
from scipy.ndimage.filters import gaussian_filter
import sim

def circular_integrate(r, F, **kwargs):
    '''
    Do a circular integral (F(r) r dr dTheta), assuming 
    '''
    return np.trapz(F * r, r, **kwargs) * np.pi * 2

# def get_power(parameters, y_grad):

def get_r(parameters):
    dr = parameters['dr']
    nr = parameters['nr']
    return np.linspace(dr / 2, nr * dr  - dr / 2, nr)

def get_z(parameters):
    dz = parameters['dz']
    nz = parameters['nz']
    return np.linspace(dz / 2, nz * dz  - dz / 2, nz)

def get_z_power(parameters, T):
    z_grad, r_grad = np.gradient(T)
    cond = get_thermal_conductivity(parameters, T)
    return circular_integrate(get_r(parameters), z_grad * cond)

def gradient(parameters, T):
    return np.gradient(T, -parameters['dz'], parameters['dr'], edge_order = 2)

def div(parameters, sigma, grad):
    r = get_r(parameters)
    z_grad2 = gradient(parameters, gaussian_filter(grad[0], sigma = sigma))[0]
    r_grad2 = gradient(parameters, gaussian_filter(r * grad[1], sigma = sigma))[1] / r
    return z_grad2 + r_grad2

def get_bp_power(parameters, T):
    r = get_r(parameters)
    cond = get_thermal_conductivity(parameters, T)
    z_grad, r_grad =  gradient(parameters, T)
    bp_inds = np.where(z_grad[0] < 0)[0]
    z_grad_bot = np.zeros(np.shape(z_grad)[1])
    z_grad_bot[bp_inds] = z_grad[0, bp_inds]
    return circular_integrate(r, cond[0] * -z_grad_bot)

def get_thermal_conductivity(parameters, T):
    z = get_z(parameters)
    hd30_inds = np.where(z <= parameters['hd30_height'])
    cond = parameters['mp24'](T)
    cond[hd30_inds] = parameters['hd30'](T[hd30_inds])
    return cond

def get_grad_magnitude(parameters, T):
    return np.sqrt(np.sum(np.array(gradient(parameters, T))**2, axis = 0))

def reshape(parameters, F):
    shape = (parameters['nz'], parameters['nr'])
    try:
        return np.reshape(F.value, shape)
    except AttributeError:
        return F.reshape(shape)

def load_sim(directory, return_all = False):
    f = open(os.path.join(directory, 'results.pkl'))
    T = pickle.load(f)
    f.close()

    f = open(os.path.join(directory, 'parameters.pkl'))
    parameters = pickle.load(f)
    f.close()
    try:
        alpha = parameters['alpha']
    except KeyError:
        parameters['alpha'] = 1.15
        alpha = parameters['alpha']
    hd30  = parameters['hd30']
    parameters['hd30'] = lambda T: (hd30 / 283.**alpha) * T**alpha
    mp24 = parameters['mp24']
    parameters['mp24'] = lambda T: (mp24 / 283.**alpha) * T**alpha
    
    if return_all:
        return parameters, T
    return parameters, reshape(parameters, T)

def do_one(directory):
    parameters, T = load_sim(directory)
    return parameters, get_bp_power(parameters, T)

def do_many(dirs, savefile = None):
    gap = np.zeros(len(dirs))
    shelf = np.zeros(len(dirs))
    alpha = np.zeros(len(dirs))
    power = np.zeros(len(dirs))
    for i, d in enumerate(dirs):
        params, power[i] = do_one(d)
        gap[i] = params['gap_radius']
        shelf[i] = params['shelf_radius']
        alpha[i] = params['alpha']
    if savefile is not None:
        np.savez_compressed(savefile, gap = gap, shelf = shelf,
                            alpha = alpha, power = power)
    return gap, shelf, alpha, power

def make_T_plot(parameters, T, savename = None):
    pl.figure()
    pl.subplot(211)
    pl.title('Gap: {:.5f}, Shelf: {:.5f}\nTemperature'.format(parameters['gap_radius'],
                                                              parameters['shelf_radius']))
    pl.imshow(T)
    pl.subplot(212)
    pl.title('Gradient')
    pl.imshow(np.log10(get_grad_magnitude(T)), vmin = -2., vmax = 2.)
    if savename is not None:
        pl.savefig(savename)
    pl.close()
    
def make_plot_2param(p1, p2, power):
    p2vals = np.unique(p2)
    pl.figure()
    for val in sorted(p2vals):
        inds = np.where(p2 == val)
        this_power = power[inds]
        this_p1 = p1[inds]
        inds = np.argsort(this_p1)
        pl.plot(this_p1[inds], this_power[inds], '.-', label = str(val))
    pl.legend()
    
def make_2d_map(p1, p2, power, return_all = False):
    p1vals = np.sort(np.unique(p1))
    p2vals = np.sort(np.unique(p2))
    outmap = np.zeros((len(p1vals), len(p2vals)))
    inds = np.argsort(p2)
    p1 = p1[inds]
    p2 = p2[inds]
    power = power[inds]
    for i, p2v in enumerate(sorted(p2vals)):
        inds = np.where(p2 == p2v)
        this_power = power[inds]
        this_p1 = p1[inds]
        inds = np.argsort(this_p1)
        this_power = this_power[inds]
        this_p1 = this_p1[inds]
        for j, pow in enumerate(this_power):
            outmap[j, i] = pow
    inds = np.where(outmap == 0)
    outmap[inds] = None
    if return_all:
        return outmap, p1vals, p2vals
    return outmap

def reshape_face(F, mesh):
    x, y = mesh.faceCenters
    xval, x_inverse = np.unique(x, return_inverse = True)
    yval, y_inverse = np.unique(y, return_inverse = True)
    # faces = F[np.array([y_inverse, x_inverse])]
    faces = np.zeros((len(yval), len(xval)))
    faces[y_inverse, x_inverse] = F
    faces[np.where(faces == 0)] = np.nan
    return faces

def _get_bp_pow_for_solve(x, params):
    '''
    Fancy shit to solve over different parameters
    `params` is a list of parameters.  `params[0]` tells us which parameter 
    we are minimizing over
    parameters:
    0: backplate radius
    1: shelf radius
    2: gap radius
    3: alpha
    4: k_hd30
    5: k_mp24
    6: cold side temp
    7: hot side temp
    '''
    x = x[0]
    if len(params) < 8:
        raise ValueError("7 input parameters!")
    args = params[1:]
    args[params[0]] = x
    # minimization_var = params[0]
    # for i in args:
    #     if i < minimization_var:
    #         args[i] = params[i + 1]
    #     if i == minimization_var:
    #         args[i] = x
    #     else:
    #         args[i] = params[i]
    outdir = tempfile.mkdtemp()
    out = sim.run_model(*args, outdir = outdir, verbose = False)
    if out is not None:
        power = do_one(outdir)[1]
    else:
        power = np.nan
    print 'power: ', power
    shutil.rmtree(outdir)
    return power

def solve_for(power, foam_rad, bp_rad, shelf_rad, bp_temp, isolve, **kwargs):
    '''
    Given a particular physical setup (foam, backplate, holder dimensions),
    a known power, and a known backplate temperature, solve for isolve.  isolve maps
    to the following parameters:
    0: backplate radius
    1: shelf radius
    2: gap radius
    3: alpha
    4: k_hd30
    5: k_mp24
    6: cold side temp
    7: hot side temp
    '''
    gap_rad = foam_rad - shelf_rad - bp_rad
    p = [isolve, bp_rad, shelf_rad, gap_rad, 1.15, .0471, .0390, 50., 300.]
    print repr(p)
    f = lambda x, p: (_get_bp_pow_for_solve(x, p) - power)**2
    bounds = ((0, None),)
        # bounds = None
    res = opt.minimize(f, 1., args = p, bounds = bounds, **kwargs)
    if res['success']:
        print "Final power: {}".format(_get_bp_pow_for_solve(res['x'], p))
    return res

# def verify(parameters, T):
#     z_grad, r_grad = gradient(T)
#     z_grad2 = np.diff

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('outfile', type = str, help = 'save file')
    parser.add_argument('directories', type = str, nargs = '+', 
                        help = 'The directories to process')
    parser.add_argument('--plots', default = None)
    args = parser.parse_args()
    if args.plots is not None:
        for d in args.directories:
            parameters, T = load_sim(d)
            make_T_plot(parameters, T, os.path.join(d, 'T-grad.png'))
    else:
        do_many(args.directories, args.outfile)
