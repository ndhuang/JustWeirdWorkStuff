import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as pl

clusterdir = "/mnt/rbfa/ndhuang/maps/clusters/"
def hist(data):
    toplot = data[np.where(data < 10)[0]]
    pl.hist(toplot, bins = 20)
    return np.median(toplot[np.where(abs(toplot - np.median(toplot)) < 2 * np.std(toplot))[0]])

def doit(field):
    dat = np.load(os.path.join(clusterdir, field, field + "_point_source_sizes.pkl"))
    fig = pl.figure()
    x = hist(dat['x_width'])    
    y = hist(dat['y_width'])
    pl.legend(['x width', 'y width'])
    ymin, ymax = pl.ylim()
    pl.vlines(x, ymin, ymax, color = 'b')
    pl.vlines(y, ymin, ymax, color = 'g')
    fig.savefig(os.path.join('/home/ndhuang/plots/ptsrc', field + '_width_hist.png'))
    
if __name__ == '__main__':
    fields = ['ra23hdec-35', 'ra1hdec-35', 'ra3hdec-35', 'ra3hdec-25']
    for f in fields:
        doit(f)
