import os, sys
import re
import argparse
import resource
import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot as pl, cm
from matplotlib.patches import Circle
import numpy as np
import sptpol_software.util.files as files
from sptpol_software.observation.sky import ang2Pix, pix2Ang
from sptpol_software.scratch.ndhuang.useful_stuff import masks
from field_centers import centers

class clusterCircler(object):
    def __init__(self, field, band, 
                 clusterdir = '/mnt/rbfa/ndhuang/maps/clusters', 
                 v = 1e-3, maskfile = None, radec0 = None):
        self.proj = 0
        self.reso = .25

        # parse field center from field name
        if radec0 is not None:
            self.radec0 = radec0
        elif field in centers.keys():
            self.radec0 = centers[field]
        else:
            match = re.match('ra(\d+)h(\d*)dec([0-9\-]+)', field)
            ra = 15 * float(match.group(1))
            if len(match.group(2)) > 0:
                ra += float(match.group(2)) / 60 * 15
            dec = float(match.group(3))
            self.radec0 = [ra, dec]

        # grab the coadd and expand it
        try:
            coadd = files.read(os.path.join(clusterdir, field, 
                                            '%03d_coadd.fits' %band))
        except IOError:
            coadd = files.read(os.path.join(clusterdir, field, 
                                            '%03dghz_coadd.fits' %band))
        self.map = coadd.coadd.map
        self.map_shape = np.shape(self.map)
        # print self.map_shape
        # self.resizeMap(2)
        
        self.contour = np.zeros(self.map_shape, dtype = int)

        self.fig = pl.figure(figsize = (9, 9), dpi = 3000)
        pl.imshow(self.map, cmap = cm.gray, vmin = -v, vmax = v, 
                  interpolation = 'None', figure = self.fig)
        sig, ra, dec, rad = \
            np.loadtxt(os.path.join(clusterdir, field, 'cluster_out', 
                                    'new', field + '_3sigma_clusters.txt'),
                              dtype = float, skiprows = 1, unpack = True)
            
        i = 0
        while sig[i] >= 4.5:
            # self.circleCluster([ra[i], dec[i]], rad[i])
            if sig[i] > 5:
                color = 'red'
            else:
                color = 'blue'
            self.addClusterToContour([ra[i], dec[i]], rad[i], color)
            i += 1
        # self.fig.set_size_inches(9, 9)
        # pl.contour(self.contour, colors = 'red', levels = [0], linewidth = .001, aa = False)
        # hot = np.argwhere(self.contour)
        # for points in hot:
        #     pl.plot(points[1], points[0], 'r.', markersize = .1, mew = 0, mec = 'r', mfc = 'r', aa = True)
        if maskfile is not None:
            mask = masks.srcMaskFromfile(maskfile, self.reso, self.map_shape,
                                      self.proj, self.radec0)
            pl.contour(mask, levels = [.9], colors = 'yellow', linewidth = .15)
        pl.savefig(os.path.join('/home/ndhuang/plots/clusters/', 
                                field + '_map.png'), 
                   bbox_inches = 'tight', pad_inches = 0,
                   dpi = 1000)
        print i

    def resizeMap(self, scale):
        scale = int(scale)
        new_map = np.zeros(self.map_shape * scale)
        for i in range(self.map_shape[0]):
            for j in range(self.map_shape[1]):
                for k in range(scale):
                    for l in range(scale):
                        new_map[i * scale + k, 
                                  j * scale + l] = self.map[i, j]
        self.map = new_map
        self.map_shape = np.shape(self.map)

    def addClusterToContour(self, radec, rad, color):
        rad /= self.reso # radius in pixels
        # rad *= 2
        y, x = ang2Pix(radec, self.radec0, self.reso, self.map_shape, 
                       self.proj, use_c_code = True, bin_center_zero = True,
                       return_validity = False)
        pl.plot(x, y, 'o', ms = rad / 2, mfc = 'none', mec = color, mew = .15, aa = False)
        for i in np.arange(-rad, rad + 1) + x:
            for j in np.arange(-rad, rad + 1) + y:
                dist2 = j**2 + i**2
                if dist2 <= rad**2 and dist2 >= (rad - 1)**2:
                    self.contour[j, i] = 1

    def circleCluster(self, radec, rad):
        rad /= self.reso # radius in pixels
        # rad *= 2
        y, x = ang2Pix(radec, self.radec0, self.reso, self.map_shape, 
                       self.proj, use_c_code = True, bin_center_zero = True,
                       return_validity = False)
        c = Circle([x, y], radius = rad + 2, edgecolor = 'r', 
                   facecolor = 'none',
                   figure = self.fig, lw = .1, clip_on = True, aa = False)
        self.fig.axes[0].add_patch(c)
        return c

    def getFig(self):
        return self.fig

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('field', type = str)
    parser.add_argument('--ptsrc', type = str, default = None)
    parser.add_argument('--band', type = int, default = None)
    args = parser.parse_args()
    if args.band is None:
        args.band = [90, 150]
    else:
        args.band = [args.band]
    for b in args.band:
        c = clusterCircler(args.field, b, clusterdir = '/mnt/rbfa/ndhuang/maps/clusters/run1_bad_ps/', maskfile = args.ptsrc)
    # fig = c.getFig()
    # pl.imshow(c.contour, interpolation = 'None', cmap = cm.gray)
    # pl.show()
