import os, sys
import argparse
import cPickle as pickle
from multiprocessing import Pool
import time
import fipy
import numpy as np

def run_model(bp_radius, shelf_radius, gap_radius, 
              alpha = 1.15, k_hd30 = .0471, k_mp24 = .0390, cold = 50., hot = 300.,
              outdir = None,  verbose = True, max_fev = 2000,
              dr = .001, dz = .001, foam_h = 25.4e-3 * 4, units = 'SI'):
    '''
    Everything is SI units for now.
    '''
    t0 = time.time()
    ###########################################################################
    # Some parameters.  These are things I probably shouldn't change.
    # HD30 height
    # hd30_h = 1 * 25.4e-3
    hd30_h = foam_h + 1
    # Foam thermal conductivity
    # HD30 .0471 W/m*K at 283 K
    # MP24 .0390 W/m*K at 283 K
    hd30 = lambda T: (k_hd30 / 283**alpha) * T**alpha
    mp24 = lambda T: (k_mp24 / 283**alpha) * T**alpha
    ###########################################################################
    foam_radius = bp_radius + shelf_radius + gap_radius
    nr = int(foam_radius / dr)
    nz = int(foam_h / dz)
    parameters = {'hot': hot, 'cold': cold, 'hd30_height': hd30_h,
                  'hd30': hd30(283), 'mp24': mp24(283), 'alpha': alpha,
                  'bp_radius': bp_radius, 'foam_radius': foam_radius,
                  'shelf_radius': shelf_radius, 'gap_radius': gap_radius, 
                  'dr': dr, 'dz': dz, 'nr': nr, 'nz': nz,
                  'foam_height': foam_h, 'units': units}
    if verbose:
        print 'backplate:\t{:.3f} m\nfoam:\t\t{:.3f} m\ngap:\t\t{:.4f} m'.format(bp_radius, foam_radius, gap_radius)

    mesh = fipy.meshes.CylindricalGrid2D(nr = nr, Lr = foam_radius, nz = nz, Lz = foam_h)
    T = fipy.CellVariable(name = 'Temperature', mesh = mesh, 
                          value = hot, hasOld = True)
    # Set constrai nts: top sides and shelf at 300 K
    # bp at 50 K
    T.constrain(hot, mesh.facesTop)
    T.constrain(hot, mesh.facesRight)
    x, y, = mesh.faceCenters
    bp_mask = (x < bp_radius) & (y == 0)
    T.constrain(cold, mesh.facesBottom & bp_mask)
    if shelf_radius > 0:
        shelf_mask = (x > (bp_radius + gap_radius)) & (y == 0)
        T.constrain(hot, mesh.facesBottom & shelf_mask)


    # set the thermal conductivity for 1 in of HD30 and 3 in of MP24
    x, y, = mesh.cellCenters
    k_var = fipy.Variable(array = np.zeros(len(x)))
    T.updateOld()
    res = 10
    i = 0
    while res > 1e-3:
        k_var = fipy.Variable(array = np.zeros(len(x)))
        k_var.setValue(hd30(T), where = y <= hd30_h)
        k_var.setValue(mp24(T), where = y >= hd30_h)
        K = fipy.CellVariable(mesh = mesh, value = k_var())
        eq = fipy.DiffusionTerm(coeff = K)
        res = eq.sweep(var = T)
        T.updateOld()
        if verbose or (i % 250 == 0 and i > 0):
            print i, res
            sys.stdout.flush()
        i += 1
        if i >= max_fev:
            return None

    if verbose:
        print '{:d} iterations'.format(i)
        print 'residual: {:f}'.format(res)
        print 'Time to run: {:.1f}'.format(time.time() - t0)
    t0 = time.time()
    
    if outdir is not None:
        f = open(os.path.join(outdir, 'results.pkl'), 'w')
        pickle.dump(T, f)
        f.close()
        f = open(os.path.join(outdir, 'parameters.pkl'), 'w')
        pickle.dump(parameters, f)
        f.close()
        
    if verbose:
        print 'Time to save: {:.1f}'.format(time.time() - t0)
    return K, T

def run_one(outdir, bp_radius, shelf_rad, gap, alpha = 1.15, 
            verbose = False, dr = .0003, overwrite = False):
    outdir = os.path.join(outdir, 'bp-{:.3f}_s-{:.4f}_g-{:.4f}_a-{:.2f}'.format(bp_radius, shelf_rad, gap, alpha))
    if os.path.exists(os.path.join(outdir, 'parameters.pkl')) and not overwrite:
        print "Not overwriting {}".format(outdir)
        return
    try:
        os.makedirs(outdir)
    except OSError:
        pass
    return run_model(bp_radius, shelf_rad, gap, outdir = outdir, verbose = verbose, 
                     dr = dr, dz = dr, alpha = alpha)

def run_one_par(args, kwargs = {}):
    run_one(*args, **kwargs)
    
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('outdir', type = str, help = 'Save directory')
    parser.add_argument('--num-procs', type = int, 
                        help = 'Number of processes to run', default = 1)
    parser.add_argument('--alpha', action = 'store_true')
    parser.add_argument('--small', action = 'store_true')
    args = parser.parse_args()
    
    ##########################################################################
    # Parameters for different sims
    alpha = np.arange(0, 1.3, .05)
    if not args.small:
        # Stuff for full-size window
        bp_radius = .720 / 2
        # foam_rad = np.arange(.725, 1.0125, .0125) / 2 # .725 to 1. in .0125 increments
        shelf_rad = np.arange(0, .200 + .0125, .0125) / 2
        gap = np.arange(0, .28 + .0125, .0125) / 2
        dr = .0005
        gap[0] = 2 * dr
        if args.alpha:
            to_run = [(args.outdir, bp_radius, sr, g, a) 
                      for sr in shelf_rad 
                      for g in gap for a in alpha]
        else:
            to_run = [(args.outdir, bp_radius, sr, g) 
                      for sr in shelf_rad for g in gap]
    if args.small:
        # Small window
        foam_rad = 13.5 * 25.4e-3 / 2
        bp_radius = np.array([8.125, 10, 11]) * 25.4e-3 / 2
        shelf_radius = .75 * 25.4e-3
        gap = foam_rad - bp_radius - shelf_radius
        if args.alpha:
            to_run = [(args.outdir, bpr, shelf_radius, g, a) 
                      for bpr, g in zip(bp_radius, gap) 
                      for a in alpha]
        else:
            to_run = [(args.outdir, bpr, shelf_radius, g) 
                      for bpr, g in zip(bp_radius, gap)]
    ##########################################################################

    if args.num_procs > 1:
        pool = Pool(args.num_procs)
        pool.map(run_one_par, to_run, chunksize = 1)
    else:
        for i, arg in enumerate(to_run):
            run_one(*arg, verbose = True)
            # if i == 5:
            #     sys.exit()
