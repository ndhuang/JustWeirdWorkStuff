import argparse
import os
import cPickle as pickle
import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as pl
from tidbits import plot_dir_to_tex as texplot

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

def doWeightReport(field, band, texfile):
    maps, med, tot, rms = loadStats(os.path.join('/mnt/rbfa/ndhuang/maps/clusters', field, "map_stats_{:03d}ghz.pkl".format(band)))
    f = open(os.path.join('/mnt/rbfa/ndhuang/maps/clusters', field, "{:03d}ghz_runlist.txt".format(band)))
    good_maps = f.read()
    good_maps = good_maps.split()
    good = np.where([m in good_maps for m in maps])[0]
    fig = pl.figure()
    pl.hist(med[good], bins = 15)
    pl.title('Median Weight of Good Maps')
    fig.savefig(os.path.join('/home/ndhuang/plots/clusters/weight_check', "median_{}_{:03d}ghz.png".format(field, band)))
    fig.clear()
    pl.hist(tot[good], bins = 15)
    pl.title('Total Weight of Good Maps')
    fig.savefig(os.path.join('/home/ndhuang/plots/clusters/weight_check', "total_{}_{:03d}ghz.png".format(field, band)))
    pl.close(fig)

    texfile.write(texplot.fig_tmpl % {'fig_file': os.path.join('/home/ndhuang/plots/clusters/weight_check', "median_{}_{:03d}ghz.png".format(field, band))})
    texfile.write(texplot.fig_tmpl % {'fig_file': os.path.join('/home/ndhuang/plots/clusters/weight_check', "total_{}_{:03d}ghz.png".format(field, band))})
    texfile.write("\\begin{tabular}{|l|r|r|}\n\
\\hline\n\
Statistic     & Minimum & Maximum \\\\\n\
\\hline\n\
Median Weight & %0.2E   & %0.2E   \\\\\n\
Total Weight  & %0.2E   & %0.2E   \\\\\n\
\\hline\n\
\end{tabular}\n\
\\clearpage\n" %(min(med[good]), max(med[good]),
               min(tot[good]), max(tot[good])))
    return os.path.join('/home/ndhuang/plots/clusters/weight_check'\
, "weight_summary.tex")


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('filename', help = 'The file')
    # args = parser.parse_args()
    # maps, med, tot, rms = loadStats(args.filename)
    texfile = open(os.path.join('/home/ndhuang/plots/clusters/weight_check', "weight_summary.tex"), 'w')
    texfile.write(texplot.preamble_tmpl %{'fig_dir': '/home/ndhuang/plots/clusters/weight_check'})
    for f in ['ra23hdec-35', 'ra1hdec-35', 'ra3hdec-35', 'ra3hdec-25']:
        texfile.write("\\section{%s}\n" %f)
        for b in [150, 90]:
            texfile.write("\\subsection{%d GHz}\n" %b)
            doWeightReport(f, b, texfile)
    
    texfile.write("\\end{document}\n")
    texfile.close()
