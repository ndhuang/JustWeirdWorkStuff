import cPickle as pickle
import os
import glob

def loadDir(directory):
    files = glob.glob(os.path.join(directory, '*.pkl'))
    data = [[] for f in files]
    for i, f in enumerate(files):
        f = open(f, 'r')
        data[i] = pickle.load(f)
        f.close()
    freq = data[0][1]
    psds = [[] for d in data]
    for i, d in enumerate(data):
        psds[i] = d[0]
    return psds, freq

def coaddPSDs(psds, goodts = [0, 1, 2, 5, 7]):
    megapsd = None
    for j in goodts:
        if megapsd is None:
            megapsd = psds[j]
        else:
            megapsd += psds[j]
    return megapsd

if __name__ == '__main__':
    import sys
    psds, freq = loadDir(sys.argv[1])
    megapsd = coaddPSDs(psds)
