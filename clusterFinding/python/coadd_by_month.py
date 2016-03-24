import os
import argparse
import glob
import re
from sptpol_software.util import files

def readRunlist(runlist):
    return sorted(open(runlist, 'r').read().split()[2:]) # yay for one-liners

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('runlist', type = str)
    parser.add_argument('output', type = str)
    parser.add_argument('--overwrite', action = 'store_true', default = False)
    # parser.add_argument('--band', type = int, default = None, nargs = '+')
    args = parser.parse_args()
    # if args.band is None:
    #     args.band = [90, 150]
    
    mapfiles = sorted(readRunlist(args.runlist))
    year = 0
    month = 0
    coadd = None
    for mf in mapfiles:
        mf = mf.strip()
        bn = os.path.basename(mf)
        new_year = bn[18:22]
        new_month = bn[22:24]
        if new_month != month or new_year != year:
            print year + month
            if coadd is not None:
                outname = os.path.join(args.output, 
                                       '{}{}.h5'.format(year, month))
                coadd.writeToHDF5(outname, overwrite = args.overwrite)
            try:
                coadd = files.read(mf)
            except IOError, err:
                print err
                continue
            year = new_year
            month = new_month
        else:
            try:
                coadd += files.read(mf)
            except IOError, err:
                print err
