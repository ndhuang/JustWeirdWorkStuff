import os, glob
import sptpol_software.util.files as files
from sptpol_software.analysis import cuts

datadir = '/data/ndhuang/auxdata/idf/ra5hdec-35/'
psfile = '/home/ndhuang/spt_code/sptpol_software/config_files/ptsrc_config_ra5hdec-35_combined.txt'
glitchargs = {'ps_list': psfile, 'n_ps': 10, 'method': 1}
cutter = cuts.Cutter()
allfiles = glob.glob(os.path.join(datadir, 'data', '*.h5'))
for f in allfiles:
    base = os.path.basename(f)
    print base
    idf = files.read(f)
    cutter.flagTimestreamJumps(idf, **glitchargs)
    idf.writeToHDF5(f, as_stub = False, overwrite = True)
    idf.writeToHDF5(os.path.join(datadir, "sim", f), as_stub = True, overwrite = True)
