import glob
import os, sys
import cPickle as pickle
import numpy as np
from scipy.ndimage import filters
from sptpol_software.util import files

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
    if rem_weight:
        not_zero = np.nonzero(map.Map.weight_map)
        map.Map.real_map_T = (map.Map.real_map_T[not_zero] / 
                              map.Map.weight_map[not_zero])
    smooth_w = filters.uniform_filter(map.Map.weight_map, size = 4)
    smooth_T = filters.uniform_filter(map.Map.real_map_T, size = 4)
    good = np.where(map.Map.weight_map > w_thresh)
    # if np.shape(good)[1] == 0:
    #     # no good indices...
    #     raise ValueError('%s has no weights greater than %d!'
    #                      %(map.from_filename, w_thresh)) 

    med_w = np.median(map.Map.weight_map[good])
    tot_w = np.sum(map.Map.weight_map[good])
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

def cutMaps(stats):
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
    args = parser.parse_args()
    if args.band is None:
        args.band = ['150ghz', '090ghz']
    else:
        args.band = ['%03dghz' %args.band]
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
                map = files.read(mf)
                try:
                    stats.update(getStats(map))
                except ValueError, err:
                    print err
            f = open(os.path.join(args.output_dir, 
                                  'map_stats_' + band + '.pkl'), 'w')
            pickle.dump(stats, f)
            f.close()
        else:
            raise NotImplementedError()
        if not args.cuts:
            sys.exit(0)
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
