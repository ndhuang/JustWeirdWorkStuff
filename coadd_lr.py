import sys, glob, os
from sptpol_software.util import files

if __name__ == '__main__':
    mapdir = sys.argv[1]
    mapfiles_left = glob.glob(os.path.join(mapdir, 'left', '*.h5'))
    coadd_dir = os.path.join(mapdir, 'coadds')
    if not os.path.exists(coadd_dir):
        os.makedirs(coadd_dir)
    
    for mf_l in mapfiles_left:
        mapname = os.path.basename(mf_l)
        mf_r = os.path.join(mapdir, 'right', mapname)
        if not os.path.exists(mf_r):
            continue
        map_l = files.read(mf_l)
        map_r = files.read(mf_r)
        try:
            full_map = map_l + map_r
        except ValueError, err:
            print mapname
            import IPython
            IPython.embed()
        full_map.writeToHDF5(os.path.join(coadd_dir, mapname))
