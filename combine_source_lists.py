import argparse
import os
import numpy as np

class PtsrcList(object):
    @staticmethod
    def fromFile(filename, with_flux = False):
        if with_flux:
            index, ra, dec, rad, flux = np.loadtxt(filename, skiprows = 2,
                                                   unpack = True)
        else:
            index, ra, dec, rad = np.loadtxt(filename, skiprows = 2,
                                             unpack = True)
            flux = None
        return PtsrcList(ra, dec, rad, flux)            
        
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

    def __init__(self, ra, dec, rad, flux = None):
        self.ra = ra
        self.dec = dec
        self.rad = rad
        self.flux = flux
        
    def findNearest(self, ra, dec):
        '''
        Find the object nearest to (RA, dec)
        '''
        mindist = 181
        i = 0
        for sra, sdec in zip(self.ra, self.dec):
            dist = self._greatCircleDist(ra, dec, sra, sdec)
            if dist < mindist:
                closest = i
                mindist = dist
            i += 1
        return closest, mindist
    
    def toDS9(self, filename):
        f = open(filename, 'w')
        f.write('index\tra\tdec\ttype\n')
        for i, (ra, dec) in enumerate(zip(self.ra, self.dec)):
            f.write('{index}\t{ra}\t{dec}\tptsrc\n'.format(index = i, ra = ra, 
                                                    dec = dec))
        f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ptsrc_lists', nargs = '+',
                        help = "The point source lists to be combined.  2+")
    parser.add_argument('--output', '-o', type = str, 
                        default = 'ptsrc_config_combined.txt',
                        help = 'The file to save the combined point source list')
    parser.add_argument('--dist', '-d', type = float, default = 2.,
                        help = 'The distance under which to consider ptsrcs matched. arcmin')
    parser.add_argument('--flux', action = 'store_true',
                        help = "All ptsrc lists have flux")
    args = parser.parse_args()
    args.dist /= 60  # degrees
    pls = [PtsrcList.fromFile(fn, with_flux = args.flux) for fn in args.ptsrc_lists]
    # find the longest list
    list_length = lambda pl: len(pl.ra)
    longest = np.argmax(map(list_length, pls))
    main = pls.pop(longest)
    ras = main.ra.copy().tolist()
    decs = main.dec.copy().tolist()
    rads = main.rad.copy().tolist()
    for pl in pls:
        j = 0
        for ra, dec, in zip(pl.ra, pl.dec):
            # print "Looking for sources near ({:6.2f}, {:5.2f})".format(ra, dec)
            i, dist = main.findNearest(ra, dec)
            # print "Nearest source is        ({:6.2f}, {:5.2f}), with a distance of {:0.2f} arcmin".format(main.ra[i], main.dec[i], dist * 60)
            # print "============================================="
            if dist < pl.rad[j]:
                ras[i] = np.mean([main.ra[i], ra])
                decs[i] = np.mean([main.dec[i], dec])
                rads[i] = max(main.rad[i], pl.rad[j])
            else:
                ras.append(pl.ra[j])
                decs.append(pl.dec[j])
                rads.append(pl.rad[j])
            j += 1
    outfile = open(args.output, 'w')
    outfile.writelines(["VALIDITYBEG 0\n", "VALIDITYEND NEXT\n",
                        "###########################################################\n",
                        "# {}\n".format(args.output),
                        "# This file contains RA, dec and mask radius for\n",
                        "# point sources from the following lists:\n"])
    outfile.writelines(["# {}\n".format(os.path.basename(fn)) 
                        for fn in args.ptsrc_lists])
    outfile.writelines(["###########################################################\n",
                        "# Index RA              DEC             Radius\n",
                        "#       (deg)           (deg)           (deg)\n"])
    i = 1
    for ra, dec, rad in zip(ras, decs, rads):
        outfile.write("{index:4d}    {ra:9.5f}     {dec:9.5f}       {rad:06.4f}\n".format(index = i, ra = ra, dec = dec, rad = rad))
        i += 1
    outfile.close()
    
                        
