import os
import re
import argparse
from datetime import datetime
from multiprocessing import Process
import numpy as np
from sptpol_software.util import files
from sptpol_software.observation.sky import ObservedSky

def coaddBundle(mapfiles, output_name, pad_to = None, overwrite = True):
    coadd = files.read(mapfiles[0])
    for mfile in mapfiles[1:]:
        m = files.read(mfile)
        coadd += m
    # pad the map
    if pad_to is not None:
        args = coadd.initargs(noshape = True)
        weight_full = np.zeros(pad_to)
        map_full = np.zeros(pad_to)
        pad = [(pt - ms) / 2 for pt, ms in zip(pad_to, coadd.shape)]
        weight_full[pad[0]:pad[0] + coadd.shape[0], 
                    pad[1]:pad[1] + coadd.shape[1]] = weight_map
        map_full[pad[0]:pad[0] + coadd.shape[0], 
                 pad[1]:pad[1] + coadd.shape[1]] = sum_map
        coadd = ObservedSky(map = map_full, weight = weight_full)
    coadd.writeToHDF5(output_name, overwrite = overwrite)
        
    info = open(output_name + '.info', 'w')
    info.write('%d\n' %len(mapfiles))
    info.write('\n'.join(mapfiles))
    info.close()

def paralellCoadd(mapfiles, mapinds, output_dir, band,
                  nprocs = 1, pad_to = None, names = None):
    mapfiles = np.asarray(mapfiles)
    if names is None:
        i = 1
        while len(mapinds) / (10**i) > 1:
            i += 1
        name_patt = "bundle_{:0{ndigits}d}_{band:03d}.h5".format(ndigits = i, band = band)
        names = [name_patt.format(i) for i in range(len(mapinds))]
    if nprocs == 1:
        for i, name in enumerate(names):
            coaddBundle(mapfiles[mapinds[i]], name, pad_to = pad_to)
            print "Completed bundle {:d} of {:d}".format(i, len(names)),
            print '\r',
    else:
        msg_freq = nprocs
        i = 0
        while i < len(names):
            procs_running = 0
            procs = [None for p in range(nprocs)]
            while procs_running < nprocs and i < len(names):
                procs[procs_running] = Process(target = coaddBundle, 
                                              args = (mapfiles[mapinds[i]], 
                                                      os.path.join(output_dir, 
                                                                   names[i]),
                                                      pad_to))
                procs[procs_running].start()
                procs_running += 1
                i += 1
            for p in procs:
                if p is not None:
                    p.join()
            print "Completed bundle {:d} of {:d}".format(i, len(names)),
            print '\r',
    print ''

def readRunlist(runlist):
    runlist = open(runlist, 'r')
    mapfiles = runlist.readlines()
    i = 0
    while i < len(mapfiles):
        mapfiles[i] = mapfiles[i].strip()
        if not os.path.exists(mapfiles[i]):
            mapfiles.pop(i)
        else:
            i += 1
    return mapfiles

def randomBundles(args, pad_to = None):
    mapfiles = readRunlist(args.runlist)
    nmaps = len(mapfiles) / args.num_bundles
    available_inds = range(len(mapfiles))
    map_inds = np.zeros((args.num_bundles, n_maps), dtype = int)
    for i in range(args.num_bundles):
        for j in range(n_maps):
            ind = np.random.randint(0, len(available_inds))
            map_inds[i, j] = available_inds.pop(ind)
    paralellCoadd(mapfiles, map_inds, args.outdir, args.band, nprocs = args.procs, pad_to = pad_to)

def azimuthBundles(args, pad_to = None):
    mapfiles = readRunlist(args.runlist)
    maptimes = map(getTimeFromFilename, mapfiles)
    maphours = [mt.hour for mt in maptimes]
    bins = range(0, 24, args.num_hours)
    bininds = np.digitize(maphours, bins) - 1
    mapinds = [np.where(bininds == bin)[0] for bin in range(len(bins))]
    names = ["{:02d}h_{:03d}ghz.h5".format(hour, args.band) for hour in bins]
    paralellCoadd(mapfiles, mapinds, args.outdir, args.band, nprocs = args.procs, 
                  pad_to = pad_to, names = names)
    
def getTimeFromFilename(filename):
    match = re.search("(\d{8}_\d{6})", os.path.basename(filename))
    if match is None:
        print os.path.basename(filename)
    return datetime.strptime(match.group(0), "%Y%m%d_%H%M%S")
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Coadd the bundles')
    # parser.add_argument('bundle_type', type = str, choices = [],
    #                     help = "The type of bundles to create")
    parser.add_argument('--band', type = int, default = None)
    parser.add_argument('--procs', type = int, default = 1)
    parser.add_argument('runlist', type = str)
    parser.add_argument('outdir', type = str)

    subparsers = parser.add_subparsers(help = "The different types of bundles that can be created", dest = 'command_name')
                                       
    rand_parser = subparsers.add_parser("random", help = "Bundle randomly")
    rand_parser.add_argument('num_bundles', type = int,
                             help = "The number of bundles to make")
    rand_parser.set_defaults(func = randomBundles)

    az_parser = subparsers.add_parser('az', help = "Bundle by starting azimuth")
    az_parser.add_argument('num_hours', type = int, 
                           help = "The RA width per bundle, in hours")
    az_parser.set_defaults(func = azimuthBundles)
    args = parser.parse_args()

    if args.band is None:
        bands = [150, 90]
    else:
        bands = [args.band]
    for band in bands:
        args.band = band
        args.func(args)
