'''
History thus far (2013 09 03):
bad run (incorrect random selection)
    /data39/ndhuang/clusters/ra23h30dec-55/maps/run1/fits/borked/
better run (contains nans)
    /data39/ndhuang/clusters/ra23h30dec-55/maps/run1/fits/bundles_v0/
'''

import os, sys, glob, pickle
import argparse
import pyfits as fits
from datetime import datetime
from multiprocessing import Process

import numpy as np
import IPython
from matplotlib import pyplot as pl, cm
from sptpol_software.util import files, fits as sptfits

def coadd_bundle(n_maps, mapfiles, output_name, map_shape, 
                 sample_fitsfile = '/data/cr/map_ra23h30dec-55_90_20100512_201429_20100513_013114.fits'):
    sum_map = np.zeros(map_shape)
    weight_map = np.zeros(map_shape)
    bundled_maps = []
    sample_fits = fits.open(sample_fitsfile)
    for i in range(n_maps):
        if len(mapfiles) < 1:
            raise RuntimeError('Oh Shit!  We\'re out of maps!')
        ind = np.random.randint(0, len(mapfiles))
        mfile = mapfiles.pop(ind)
        bundled_maps.append(mfile)
        m = files.read(mfile)
        sum_map += m.Map.real_map_T * m.Map.weight_map
        weight_map += m.Map.weight_map
    
    # handle 0s in the weight map
    inds = np.nonzero(weight_map)
    sum_map[inds] /= weight_map[inds]
    inds = np.nonzero(weight_map == 0)
    sum_map[inds] = 0
    sptfits.writeSptFits(output_name + '.fits', overwrite = True, 
                         map = sum_map, weight = weight_map, 
                         mapinfo = sample_fits['mapinfo'],
                         processing = sample_fits['processing'])
    info = open(output_name + '.info', 'w')
    info.write('%d\n' %n_maps)
    info.write('\n'.join(bundled_maps))
    info.close()
    return mapfiles

def coadd_bundle_paralell(map_inds, mapfiles, output_name, 
                          map_shape = (3400,3400), 
                          sample_fitsfile = '/data/cr/map_ra23h30dec-55_90_20100512_201429_20100513_013114.fits'):
    mapfiles = np.asarray(mapfiles)
    sum_map = np.zeros(map_shape)
    weight_map = np.zeros(map_shape)
    bundled_maps = mapfiles[map_inds]
    sample_fits = fits.open(sample_fitsfile)
    for mfile in bundled_maps:
        m = files.read(mfile)
        try:
            sum_map += m.Map.real_map_T * m.Map.weight_map
        except AttributeError:
            print m
            print mfile
        weight_map += m.Map.weight_map
    
    # handle 0s in the weight map
    inds = np.nonzero(weight_map)
    sum_map[inds] /= weight_map[inds]
    inds = np.nonzero(weight_map == 0)
    sum_map[inds] = 0
    # this is writing fits files with map.weight.weight
    # we'd like map.weight.map
    sptfits.writeSptFits(output_name + '.fits', overwrite = True, 
                         map = sum_map, weight = weight_map, 
                         mapinfo = sample_fits['mapinfo'],
                         processing = sample_fits['processing'])
    info = open(output_name + '.info', 'w')
    info.write('%d\n' %n_maps)
    info.write('\n'.join(bundled_maps))
    info.close()

if __name__ == '__main__':
    # directory = sys.argv[1]
    # outdir = sys.argv[2]
    parser = argparse.ArgumentParser(description = 'Coadd the bundles')
    parser.add_argument('--num_procs', type = int, default = 1)
    parser.add_argument('--num_bundles',  type = int, default = 100)
    parser.add_argument('directory', type = str)
    parser.add_argument('outdir', type = str)
    args = parser.parse_args()

    # use abby's bundles for now
    # mapfiles = glob.glob(os.path.join(args.directory, '*150ghz.hdf5'))
    bundle_file = open('/home/nlharr/bundles_150GHz_v2_runlist.pkl', 'r')
    bundle_info = pickle.load(bundle_file)[0]
    bundle_file.close()
    mapfiles = []
    for v in bundle_info.itervalues():
        mapfiles += v
    i = 0
    while i < len(mapfiles):
        mapfiles[i] = os.path.join(args.directory, 
                                   mapfiles[i] + '_150ghz.hdf5')
        if not os.path.exists(mapfiles[i]):
            mapfiles.pop(i)
        else:
            i += 1
            
        

    n_bundles = args.num_bundles
    n_maps = len(mapfiles) / n_bundles
    available_inds = range(len(mapfiles))
    map_inds = np.zeros((n_bundles, n_maps), dtype = int)
    for i in range(n_bundles):
        for j in range(n_maps):
            ind = np.random.randint(0, len(available_inds))
            map_inds[i, j] = available_inds.pop(ind)

    if args.num_procs == 1:
        for i, inds in enumerate(map_inds):
            outname = args.outdir + 'bundle_%02d_150ghz' %i
            coadd_bundle_paralell(inds, mapfiles, outname)
    else:
        i = 0
        while i < n_bundles:
            running_procs = 0
            procs = [[] for p in range(args.num_procs)]
            while running_procs < args.num_procs and i < n_bundles:
                outname = args.outdir + 'bundle_%02d_150ghz' %i
                procs[running_procs] = Process(target = coadd_bundle_paralell, 
                                               args = (map_inds[i], mapfiles, 
                                                       outname))
                procs[running_procs].start()
                running_procs += 1
                i += 1
            for p in procs:
                p.join()
            print 'Completed bundle %d of %d %s' %(i, n_bundles, 
                                                   datetime.now().strftime('%H:%M'))
                                  
    # for i in range(n_bundles):
    #     try:
    #         bundle_filename = args.outdir + 'bundle_%02d_150ghz' %i
    #         mapfiles = coadd_bundle(n_maps, mapfiles, bundle_filename, (3400,3400))
    #         print 'Completed bundle %d of %d %s' %(i, n_bundles, 
    #                                                datetime.now().strftime('%H:%M'))
    #     except IndexError, err:
    #         print err
    #         print 'Number of mapfiles left: ' + str(len(mapfiles))
            
