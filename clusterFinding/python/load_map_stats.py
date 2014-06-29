import argparse
import cPickle as pickle
import numpy as np

def loadStats(filename):
    f = open(filename, 'r')
    stats = pickle.load(f)
    f.close()
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help = 'The file')
    args = parser.parse_args()
    maps, med, tot, rms = loadStats(args.filename)
