import glob
import os
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
    if w_thresh == 0:
        raise RuntimeError("We fucked up!!!" + map.from_filename)
    good = np.where(map.Map.weight_map > w_thresh)
    # if np.shape(good)[1] == 0:
    #     # no good indices...
    #     raise ValueError('%s has no weights greater than %d!'
    #                      %(map.from_filename, w_thresh)) 

    med_w = np.median(map.Map.weight_map[good])
    tot_w = np.sum(map.Map.weight_map[good])
    rms = np.sqrt(np.sum(smooth_T[good]**2))
    return {map.from_filename: {'rms': rms, 'med_w': med_w, 'tot_w': tot_w}}

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
    args = parser.parse_args()
    if args.band is None:
        args.band = ['150ghz', '090ghz']
    else:
        args.band = ['%03d' %args.band]
    if args.output_dir is None:
        args.output_dir = args.map_dir

    for band in args.band:
        stats = {}
        map_files = glob.glob(os.path.join(args.map_dir, '*' + band + '.h5'))
        for mf in map_files:
            map = files.read(mf)
            try:
                stats.update(getStats(map))
            except ValueError, err:
                print err
        f = open(os.path.join(args.output_dir, 'map_stats_' + band + '.pkl'),
                 'w')
        pickle.dump(stats, f)
        f.close()
