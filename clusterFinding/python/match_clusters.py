import argparse
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as pl

class ObjectList(object):
    @staticmethod
    def fromFile(filename, skiprows = 1, **kwargs):
        sig, ra, dec, rad = np.loadtxt(filename, skiprows = skiprows, 
                                       unpack = True, **kwargs)
        return ObjectList(sig, ra, dec, rad)

    @staticmethod
    def _wrap(ra):
        # force an angle to be between 0 and 180
        if abs(ra) > 180:
            if ra > 0:
                return ra - 180
            else:
                return ra + 180
        return ra
    
    @staticmethod
    def _greatCircleDist(ra1, dec1, ra2, dec2):
        ra1 = np.deg2rad(ra1)
        dec1 = np.deg2rad(dec1)
        ra2 = np.deg2rad(ra2)
        dec2 = np.deg2rad(dec2)
        return np.rad2deg(np.arccos(np.sin(dec1) * np.sin(dec2) + np.cos(dec1) * np.cos(dec2) * np.cos(abs(ra1 - ra2))))

    def __init__(self, sig, ra, dec, rad):
        self.sig = sig
        self.ra = ra
        self.dec = dec
        self.rad = rad
        
    def __getitem__(self, key):
        return ObjectList(self.sig[key], self.ra[key], 
                           self.dec[key], self.rad[key])

    def findNearest(self, ra, dec):
        '''
        Find the object nearest to (RA, dec)
        '''
        mindist = 181
        for sra, sdec in zip(self.ra, self.dec):
            mindist = min(self._greaCircleDist(ra, dec, sra, sdec), mindist)
        return mindist

    def compare(self, other, lim):
        matches = {}
        nomatch = {}
        i = 0
        for ra, dec in zip(self.ra, self.dec):
            found_match = False
            j = 0
            mindist = 181.
            for ora, odec in zip(other.ra, other.dec):
                dra = self._wrap(ra - ora)
                ddec = (dec - odec) * np.cos(np.mean([dec, odec]))
                dist = np.sqrt(dra*dra + ddec*ddec)
                mindist = min(dist, mindist)
                if dist < lim:
                    matches[i] = {'dist': dist, 'sig': self.sig[i], 
                                  'other_sig': other.sig[j]}
                    found_match = True
                    break
                j += 1
            if not found_match:
                nomatch[i] = {'sig': self.sig[i], 'min_dist': mindist}
            i += 1
        return matches, nomatch

    def toDS9(self, filename):
        f = open(filename, 'w')
        f.write('index\tra\tdec\tsignificance\tradius\ttype\n')
        for i, (ra, dec, sig, rad) in enumerate(zip(self.ra, self.dec, self.sig, self.rad)):
            f.write('{index}\t{ra}\t{dec}\t{sig}\t{rad}\tcluster\n'.format(index = i, ra = ra, dec = dec, sig = sig, rad = rad))
        f.close()
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser("Compare two cluster lists")
    parser.add_argument('cluster_list1', type = str,
                        help = 'The first cluster list')
    parser.add_argument('cluster_list2', type = str,
                        help = 'The second cluster list')
    parser.add_argument('--sigma', type = float, default = 4.5,
                        help = 'Compare clusters down to this significance')
    parser.add_argument('--dist', type = float, default = 2,
                        help = "The distance under which to consider two clusters a match- in arcmin")
    parser.add_argument('--plot-dir', type = str, default = None)
    parser.add_argument('--save-name', type = str, default = None)
    args = parser.parse_args()
    if not (args.cluster_list1.endswith('txt') and args.cluster_list2.endswith('txt')):
        raise NotImplementedError('I only read text files right now.')
    cl1 = ObjectList.fromFile(args.cluster_list1)
    cl2 = ObjectList.fromFile(args.cluster_list2)
    # assume clusters are sorted by significance
    num1 = len(np.where(cl1.sig > args.sigma)[0])
    num2 = len(np.where(cl2.sig > args.sigma)[0])
    num = max(num1, num2)
    cl1 = cl1[:num]
    cl2 = cl2[:num]
    
    matches, nomatch = cl1.compare(cl2, args.dist / 60.)
    dummy, nomatch2 = cl2.compare(cl1, args.dist / 60.)
    sig1 = np.zeros(len(matches))
    sig2 = np.zeros(len(matches))
    print "  sig1  |  sig2  |  distance (arcmin)"
    for i, k in enumerate(matches.keys()):
        sig1[i] = cl1.sig[k]
        sig2[i] = cl2.sig[k]
        matches[k]['dist'] *= 60 # convert to arcmin
        print " {sig:6.3f} | {other_sig:6.3f} | {dist:0.6f}".format(**matches[k])
    print "Significance of unmatched clusters:"
    print "List 1: {}".format(args.cluster_list1)
    print "  sig   |   ra   |  dec   | Nearest neighbor (arcmin)"
    for k in nomatch.keys():
        print " {sig:6.3f} | {ra:6.2f} | {dec:6.2f} | {dist:6.2f}".format(sig = cl1.sig[k], ra = cl1.ra[k], dec = cl1.dec[k], dist = nomatch[k]['min_dist'] * 60)
    print "List 2: {}".format(args.cluster_list2)
    print "  sig   |   ra   |  dec   | Nearest neighbor (arcmin)"
    for k in nomatch2.keys():
        print " {sig:6.3f} | {ra:6.2f} | {dec:6.2f} | {dist:6.2f}".format(sig = cl2.sig[k], ra = cl2.ra[k], dec = cl2.dec[k], dist = nomatch2[k]['min_dist'] * 60)

    pl.plot(sig1, sig2, '.', label = '_nolegend_')
    xmin, xmax = pl.xlim()
    ymin, ymax = pl.ylim()
    top = max(xmax, ymax)
    bot = min(xmin, ymin)
    pl.plot([bot, top], [bot, top], '--k', label = '1:1')
    pl.xlim(xmin, xmax)
    pl.ylim(ymin, ymax)
    pl.legend(loc = 'upper left')
    pl.title('Sig-Sig Cluster List Comparison')
    if args.save_name is not None:
        pl.savefig(os.path.join(args.plot_dir, args.save_name))
    
