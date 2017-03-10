import glob
import os, sys
import time
import cPickle as pickle
import numpy as np
from scipy.ndimage import filters
from sptpol_software.util import files
# from sptpol_software.observation.sky import ang2Pix

def writeRunlist(files, runfilename):
    runfile = open(runfilename, 'w')
    runfile.write('1 %d\n' %len(files))
    runfile.write('Set 1:\n')
    for mf in files:
        runfile.write(mf + '\n')
    runfile.close()

def getStats(map, w_thresh = .3, rem_weight = False):
    # rms is calculated on a map smoothed with a 1-arcmin box car
    # only take points where weight > threshold
    # remove the weight first
    
    # This is for pure c maps, not loaded into a map object
    # if rem_weight:
    #     not_zero = np.nonzero(map.Map.weight_map)
    #     map.Map.real_map_T = (map.Map.real_map_T[not_zero] / 
    #                           map.Map.weight_map[not_zero])
    # smooth_w = filters.uniform_filter(map.Map.weight_map, size = 4)
    # smooth_T = filters.uniform_filter(map.Map.real_map_T, size = 4)
    # if len(np.shape(map.Map.weight_map)) > 2:
    #     # for polarized maps
    #     good = np.where(map.Map.weight_map[:,:, 0, 0] > w_thresh)
    # else:
    #     good = np.where(map.Map.weight_map > w_thresh)
    # med_w = np.median(map.Map.weight_map[good])
    # tot_w = np.sum(map.Map.weight_map[good])
    # rms = np.sqrt(np.sum(smooth_T[good]**2))
    
    # This is for sptpol-style map objects
    if map.weighted_map:
        map.removeWeight()
    smooth_w = filters.uniform_filter(map.weight, size = 4)
    smooth_T = filters.uniform_filter(map.map, size = 4)
    good = np.where(map.weight > w_thresh)
    
    med_w = np.median(map.weight[good])
    tot_w = np.sum(map.weight[good])
    rms = np.sqrt(np.sum(smooth_T[good]**2))
    return {map.from_filename: {'rms': rms, 'med_w': med_w, 'tot_w': tot_w}}

def loadStats(stats):
    N = len(stats.keys())
    mapname = ['' for k in stats.keys()] # in case dict ordering changes
    med_w = np.zeros(N)
    tot_w = np.zeros(N)
    rms = np.zeros(N)
    for i, key in enumerate(stats.keys()):
        mapname[i] = key
        med_w[i] = stats[key]['med_w']
        tot_w[i] = stats[key]['tot_w']
        rms[i] = stats[key]['rms']
    
    mapname = np.array(mapname)
    inds = np.where(np.bitwise_not(np.isnan(med_w)))
    mapname = mapname[inds]
    med_w = med_w[inds]
    tot_w = tot_w[inds]
    rms = rms[inds]
    return mapname, med_w, tot_w, rms

def getDSStats(sptpolmap, w_thres = .3):
    sources_real = [[359.478, -53.1902], # RA, dec for sources to check
                    [348.942, -50.3142],
                    [352.345, -49.931],]
    sources_diff = [[359.455719, -53.188625],
                    [348.917572, -50.311596],
                    [352.322052, -49.930763]]
    sources = sources_diff
    if sources == sources_diff:
        print '=' * 50
        print 'Using diff sources'
        print '=' * 50
    sptpolmap.removeWeight()
    weight = sptpolmap.weight
    map = sptpolmap.map
    mw = np.median(weight)
    good = np.where(weight > .3 * mw)
    mgood = map[good]
    wgood = weight[good]
    rms = np.sqrt(np.sum(mgood * mgood))
    med_w = np.median(wgood)
    rms_w = np.sqrt(np.sum(wgood * wgood))
    out = {sptpolmap.from_filename: {'rms': rms, 'med_w': med_w, 'rms_w': rms_w}}
    out[sptpolmap.from_filename]['sources'] = {}
    i = 0
    for ra, dec in sources:
        pix, good = sptpolmap.ang2Pix([ra, dec], return_validity = True)
        y, x = pix
        out[sptpolmap.from_filename]['sources'][i] = sptpolmap.map[y, x]
        i += 1
    return out    

def loadDSStats(filename):
    stats = np.load(filename)
    N = len(stats.keys())
    mapname = ['' for k in stats.keys()] # in case dict ordering changes
    med_w = np.zeros(N)
    rms_w = np.zeros(N)
    rms = np.zeros(N)
    sources = np.zeros((len(stats[stats.keys()[0]]['sources'].keys()), N))
    for i, key in enumerate(stats.keys()):
        mapname[i] = key
        mapstat = stats[key]
        med_w[i] = mapstat['med_w']
        rms_w[i] = mapstat['rms_w']
        rms[i] = mapstat['rms']
        for jey in mapstat['sources'].keys():
            sources[jey, i] = mapstat['sources'][jey]
    
    mapname = np.array(mapname)
    inds = np.where(np.bitwise_not(np.isnan(med_w)))[0]
    mapname = mapname[inds]
    med_w = med_w[inds]
    rms_w = rms_w[inds]
    rms = rms[inds]
    sources = sources[:, inds]
    return mapname, med_w, rms_w, rms, sources

def cutSigma(data, thresh = 3.):
    oldn = len(data) + 1
    newn = len(data)
    inds = range(len(data))
    while newn != oldn:
        oldn = newn
        m = np.mean(data[inds])
        s = np.std(data[inds])
        inds = np.where(abs(data - m) < thresh * s)[0]
        newn = len(inds)
    return inds

def sourceCuts(sources):
    goodinds = set()
    for i in [0, 1]:
        inds = np.where(sources[i] != 0)[0]
        good = cutSigma(sources[i][inds], thresh = 3.)
        goodinds = goodinds.union(set(inds[good]))
    return list(goodinds)

def medianWeightCut(med_w):
    return cutSigma(med_w, thresh = 3.)

def rmsWeightCut(rms_w):
    return cutSigma(rms_w, thresh = 3.)

def rmsCut(rms):
    return cutSigma(rms, thresh = 3.)

def argCutMaps(statsfile):
    mapfiles, med_w, rms_w, rms, sources = loadDSStats(statsfile)
    good_maps = set(sourceCuts(sources))
    good_maps = good_maps.intersection(set(medianWeightCut(med_w)))
    good_maps = good_maps.intersection(set(rmsWeightCut(rms_w)))
    good_maps = good_maps.intersection(set(rmsCut(rms)))
    return list(good_maps)

def cutMaps(statsfile):
    mapfiles, med_w, rms_w, rms, sources = loadDSStats(statsfile)
    return mapfiles[argCutMaps(statsfile)]

def cutMapsOLD(stats):
    maps, med, tot, rms = loadStats(stats)
    inds = np.where(np.bitwise_not(np.isnan(med)))
    maps = maps[inds]
    med = med[inds]
    tot = tot[inds]
    rms = rms[inds]
    med_med = np.median(med)
    med_rms = np.median(rms)
    med_tot = np.median(tot)

    good = np.where((rms <= 3 * med_rms) & 
                    (rms >= .75 * med_rms) &
                    (med <= 1e8))[0]
    return maps[good]

if __name__ == '__main__':
    # default behavior is to calculate stats, then do cuts, then write runlist
    import argparse
    parser = argparse.ArgumentParser(description = 
                                     'Gather statistics for cutting maps')
    parser.add_argument('map_dir', type = str, 
                        help = 'The directory containing the maps')
    parser.add_argument('-b', '--band', type = int, default = None,
                        help = 'The frequency band')
    parser.add_argument('-o', '--output-dir', type = str, default = None,
                        dest = 'output_dir',
                        help = 'The directory to store statistics in')
    parser.add_argument('--no-cuts', action = 'store_false', dest = 'cuts',
                        help = 'Do not apply cuts')
    parser.add_argument('--stats-file', type = str, default = None,
                        help = 'The pickle file containing statistsics.  If set, this implies that we will not calculate statistics')
    parser.add_argument('--no-runlist', action = 'store_false', 
                         dest = 'runlist',
                         help = 'Do not write the runlist')
    parser.add_argument('--tex-file', type = str, default = None,
                        help = 'Write output to a tex file rather than stdout')
    parser.add_argument('--downsampled', action = 'store_true')
    # parser.add_argument('--bad-file' type = str, default = None,
    #                     help = "A file in which to record \"bad\" maps, and why they were cut")
    args = parser.parse_args()
    if args.band is None:
        args.band = ['150ghz', '090ghz']
    else:
        args.band = ['%03dghz' %args.band]
        # args.band = ['%03d' %args.band]
    if args.output_dir is None:
        args.output_dir = args.map_dir
    if args.tex_file is not None:
        texfile = open(args.tex_file, 'a')
        texfile.write("\\begin{tabular}{|c|c|c|}\n")
        texfile.write("\\hline\n")
        texfile.write("Band & Number of obs & Number of good maps \\\\\n")
        texfile.write("\\hline\n")
    else:
        texfile = None

    for band in args.band:
        if args.stats_file is None:
            stats = {}
            map_files = glob.glob(os.path.join(args.map_dir, 
                                               '*' + band + '.h5'))
            for mf in map_files:
                try:
                    map = files.read(mf)
                except IOError:
                    continue
                try:
                    if args.downsampled:
                        # map.weighted_map = True
                        # map.writeToHDF5(map.from_filename, overwrite = True)
                        stats.update(getDSStats(map))
                    else:
                        stats.update(getStats(map))
                except Exception, err:
                    print err
                # stats.update(getStats(map))
            f = open(os.path.join(args.output_dir, 
                                  'map_stats_' + band + '.pkl'), 'w')
            pickle.dump(stats, f)
            f.close()
        else:
            raise NotImplementedError()
        if not args.cuts:
            continue
        good_maps = cutMaps(stats)
        if texfile is None:
            print "%s: %d good maps of %d maps" %(band, len(good_maps), 
                                                  len(stats.keys())) 
        else:
            texfile.write("%s & %d & %d\\\\\n" %(band, len(good_maps), 
                                                 len(stats.keys())))
        if not args.runlist:
            sys.exit(0)
        writeRunlist(good_maps, os.path.join(args.output_dir, 
                                             band + '_runlist.txt'))
    if texfile is not None:
        texfile.write("\\hline\n\end{tabular}\n")
