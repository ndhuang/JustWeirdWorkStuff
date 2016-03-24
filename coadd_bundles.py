import os, sys
import re
import argparse
from datetime import datetime, timedelta
from multiprocessing import Process, Pool
import numpy as np
import matplotlib.pyplot as pl
from sptpol_software.util import files, log_parse as logs
from sptpol_software.util.time import SptDatetime
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

def coaddDiffBundle(mapfiles, output_name, pad_to = None, overwrite = True):
    coadd = files.read(mapfiles[0])
    plus = 1
    minus = 0
    for i, mfile in enumerate(mapfiles[1:]):
        m = files.read(mfile)
        if i % 2 == 0:
            coadd += -1 * m # subtraction works only on weighted regions
        else:
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
    print "Coadding bundles using {} processes".format(nprocs)
    mapfiles = np.asarray(mapfiles)
    if names is None:
        i = 1
        while len(mapinds) / (10**i) > 1:
            i += 1
        i += 1
        name_patt = "bundle_{{:0{ndigits}d}}_{band:03d}.h5".format(ndigits = i, band = band)
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

def paralellDiffCoadd(mapfiles, mapinds, output_dir, band,
                  nprocs = 1, pad_to = None, names = None):
    print "Coadding bundles using {} processes".format(nprocs)
    mapfiles = np.asarray(mapfiles)
    if names is None:
        i = 1
        while len(mapinds) / (10**i) > 1:
            i += 1
        i += 1
        name_patt = "bundle_{{:0{ndigits}d}}_{band:03d}.h5".format(ndigits = i, band = band)
        names = [name_patt.format(i) for i in range(len(mapinds))]
    if nprocs == 1:
        for i, name in enumerate(names):
            coaddDiffBundle(mapfiles[mapinds[i]], name, pad_to = pad_to)
            print "Completed bundle {:d} of {:d}".format(i, len(names)),
            print '\r',
            sys.exit()
    else:
        msg_freq = nprocs
        i = 0
        while i < len(names):
            procs_running = 0
            procs = [None for p in range(nprocs)]
            while procs_running < nprocs and i < len(names):
                procs[procs_running] = Process(target = coaddDiffBundle, 
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
    mapfiles = runlist.read().split('\n')
    if 'Set' in mapfiles[1]:
        # this is an IDL runlist, but we're assuming there's only one set
        mapfiles = mapfiles[2:]
    for i, mf in enumerate(mapfiles):
        mapfiles[i] = mf.strip()
    return mapfiles


def randomBundles(args, pad_to = None):
    mapfiles = readRunlist(args.runlist)
    nmaps = len(mapfiles) / args.num_bundles
    available_inds = range(len(mapfiles))
    map_inds = [[] for i in range(args.num_bundles)]
    bundle = 0
    while len(available_inds) > 0:
        bundle = bundle % args.num_bundles
        ind = np.random.randint(0, len(available_inds))
        map_inds[bundle].append(available_inds.pop(ind))
        bundle += 1
    map_inds = np.asarray(map_inds)
    paralellCoadd(mapfiles, map_inds, args.outdir, args.band, nprocs = args.procs, pad_to = pad_to)

def getLTFromRA(mapfile, thresh = .3, min_offset = 100):
    # look at the mean x-position of good pixels
    try:
        map = files.read(mapfile)
    except IOError:
        return None
    xpix = map.shape[1]
    goodpix = np.where(map.weight > thresh * np.median(map.weight))
    mean_x = np.mean(goodpix[1])
    if mean_x < xpix / 2 - min_offset:
        return 'L'
    if mean_x > xpix / 2 + min_offset:
        return 'T'
    else:
        return 'F'
        

def getLT(filename, verbose = False):
    def parseScanWidth(scan_name):
        match = re.match('scan/add .?az-(\d+)p(\d).*', scan_name)
        width = float(match.group(1)) + float(match.group(2)) / 10
        return width
        
    # only working for cluster runs right now
    bn = os.path.basename(filename)
    try:
        time = SptDatetime(bn[18:33])
    except TypeError:
        if verbose:
            print "Invalid time: " + bn[18:33]
        return getLTFromRA(filename)
    params  = logs.getFieldScanParams(time - timedelta(hours = 15), 
                                      time + timedelta(hours = 15),
                                      source = 'ra23h30dec-55')
    try:
        params = params['ra23h30dec-55']
    except KeyError:
        if verbose:
            print "No scans found"
            return getLTFromRA(filename)
    if len(params.keys()) < 1:
        if verbose:
            print "No scans found 2"
            return getLTFromRA(filename)
    keys = sorted(params.keys())
    msg = None
    for i, key in enumerate(keys):
        start = SptDatetime(params[key]['this_obs'])
        try:
            stop =  SptDatetime(params[key]['obs_end'])
        except KeyError:
            try:
                # if we put in more trys, everything will work!
                stop = SptDatetime(params[keys[i + 1]]['this_obs'])
            except IndexError:
                if verbose:
                    print "Missing this_obs or obs_end key"
                return getLTFromRA(filename)
        if start <= time and time <= stop:
            if parseScanWidth(params[key]['scan_sched']) > 11:
                # if verbose:
                #     print "Full field ob"
                return 'F'
            return params[key]['leadtrail']
    if verbose:
        if msg is None:
            print "No matching observation"
        else:
            print msg
    return getLTFromRA(filename)

def leadtrailDiffBundles(args, pad_to = None):
    mapfiles = readRunlist(args.runlist)
    if args.procs > 1:
        # pool = Pool(args.procs * 2)
        pool = Pool(20)
        leadtrails = pool.map(getLT, mapfiles)
    else:
        leadtrails = map(getLT, mapfiles)
    leadtrails = np.array(leadtrails)
    leadinds = np.where(leadtrails == 'L')[0]
    trailinds = np.where(leadtrails == 'T')[0]
    n_bad = len(leadtrails) - len(leadinds) - len(trailinds)
    print "Found {:d} obs without L or T".format(n_bad)
    np.random.shuffle(leadinds)
    np.random.shuffle(trailinds)
    nlead = len(leadinds) / args.num_bundles
    ntrail = len(trailinds) / args.num_bundles
    if nlead % 2 != 0:
        nlead -= 1
    if ntrail % 2 != 0:
        ntrail -= 1
    nobs = min(nlead, ntrail)
    map_inds = np.zeros((args.num_bundles, 2 * nobs), dtype = int)
    for i in range(args.num_bundles):
        map_inds[i] = np.array([leadinds[i * nobs : (i + 1) * nobs],
                                trailinds[i * nobs : (i + 1) * nobs]]).flatten()
    paralellDiffCoadd(mapfiles, map_inds, args.outdir, args.band, nprocs = args.procs, pad_to = pad_to)

def leadtrailBundles(args, pad_to = None):
    mapfiles = readRunlist(args.runlist)
    if args.procs > 1:
        pool = Pool(args.procs)
        # pool = Pool(10)
        leadtrails = pool.map(getLT, mapfiles)
    else:
        leadtrails = map(getLT, mapfiles)
    leadtrails = np.array(leadtrails)
    leadinds = np.where(leadtrails == 'L')[0]
    trailinds = np.where(leadtrails == 'T')[0]
    fullinds = np.where(leadtrails == 'F')[0]
    n_bad = len(leadtrails) - len(leadinds) - len(trailinds) - len(fullinds)
    if n_bad > 1:
        print "Found {:d} obs without L, T or F".format(n_bad)
    np.random.shuffle(leadinds)
    np.random.shuffle(trailinds)
    np.random.shuffle(fullinds)
    nlead = len(leadinds) / args.num_bundles
    ntrail = len(trailinds) / args.num_bundles
    nfull = len(fullinds) / args.num_bundles
    print nlead, ntrail, nfull
    map_inds = np.empty(args.num_bundles, dtype = object)
    for i in range(args.num_bundles):
        map_inds[i] = np.concatenate([leadinds[i * nlead : (i + 1) * nlead],
                       trailinds[i * ntrail : (i + 1) * ntrail]])
        if nfull > 0:
            map_inds[i] =np.concatenate([map_inds[i],
                                         fullinds[i * nfull : (i + 1) * nfull]])
    extralead = len(leadinds) % args.num_bundles
    extratrail = len(trailinds) % args.num_bundles
    extrafull = len(fullinds) % args.num_bundles
    print extralead, extratrail, extrafull
    bundle = 0
    for i in range(extralead):
        map_inds[bundle] = np.concatenate([map_inds[bundle], 
                                           np.array([leadinds[args.num_bundles * nlead + i]])])
        bundle += 1
        bundle = bundle % args.num_bundles
    for i in range(extratrail):
        map_inds[bundle] = np.concatenate([map_inds[bundle], 
                                           np.array([trailinds[args.num_bundles * ntrail + i]])])
        bundle += 1
        bundle = bundle % args.num_bundles
    for i in range(extrafull):
        map_inds[bundle] = np.concatenate([map_inds[bundle], 
                                           np.array([fullinds[args.num_bundles * nfull + i]])])
        bundle += 1
        bundle = bundle % args.num_bundles
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
    # return datetime.strptime(match.group(0), "%Y%m%d_%H%M%S")
    return SptDatetime(match.group(0))
    

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
    
    ltparser = subparsers.add_parser("lt", help = "Bundle cluster maps in leadtrail pairs-ish")
    ltparser.add_argument('num_bundles', type = int,
                          help = "The number of bundles to make")
    ltparser.set_defaults(func = leadtrailBundles)
    args = parser.parse_args()

    if args.band is None:
        bands = [150, 90]
    else:
        bands = [args.band]
    for band in bands:
        args.band = band
        args.func(args)
