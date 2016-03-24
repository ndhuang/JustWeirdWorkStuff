import os
import argparse
import numpy as np
from sptpol_software.util import idl, files
from sptpol_software.scratch.ndhuang.useful_stuff import masks
from sptpol_software.scratch.ndhuang.catalog import Catalog
from field_centers import centers

def makeDS9ForBand(output_dir, band, map, center, reso, proj, mask = None):
    map_name = os.path.join(output_dir, "{:03d}.fits".format(band))
    masked_name = os.path.join(output_dir, "{:03d}_masked.fits".format(band))
    ra0 = center[0]
    dec0 = center[1]
    idl_input = "write_spt_map_fits, '{outname}', map, {ra0}, {dec0}, {reso}, projection = {proj}".format(outname = map_name, ra0 = ra0, dec0 = dec0, reso = reso, proj = proj)
    idl.idlRun(idl_input, map = map, return_all = True)
    if mask is not None:
        idl_input = "write_spt_map_fits, '{outname}', map, {ra0}, {dec0}, {reso}, projection = {proj}".format(outname = masked_name, ra0 = ra0, dec0 = dec0, reso = reso, proj = proj)
        idl.idlRun(idl_input, map = map * mask, return_all = True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Take the cluster results and make outputs usable with DS9')
    # parser.add_argument('field', type = str, help = "The CMB field")
    parser.add_argument('clusters')
    parser.add_argument('coadd')
    # parser.add_argument('--band', type = int, default = None,
    #                     help = 'Frequency band')
    parser.add_argument('--cluster-dir', type = str, 
                        default = '/mnt/rbfa/ndhuang/maps/clusters',
                        help = 'The directory containing the fields')
    parser.add_argument('--ptsrc', type = str, default = None,
                        help = 'The ptsrc config file')
    parser.add_argument('output', type = str,
                        help = 'The output directory')
    parser.add_argument('field')
    args = parser.parse_args()
    # if not os.path.exists(args.cluster_dir):
    #     raise IOError("Directory {} does not exist!".format(args.cluster_dir))
    # if args.band is None:
    #     args.band = [150, 90]
    # else:
    #     args.band = [args.band]
    if args.output is None:
        args.output = os.path.join(args.cluster_dir, args.field, 'ds9')
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # make source lists
    cl = Catalog.fromFilename(args.clusters, usecols = [1, 2, 3])
    cl.type = 'cluster'
    cl.toDS9(os.path.join(args.output, 'clusters.tsv'))
    if args.ptsrc is not None:
        pl = Catalog.fromFilename(args.ptsrc, skiprows = 2, header_line = -2)
        pl.type = 'ptsrc'
        pl.toDS9(os.path.join(args.output, 'ptsrc.tsv'))

    # map stuff
    map = files.read(args.coadd)
    # apod mask
    mask = files.read(args.coadd.replace('coadd', 'mask'))
    map.coadd.map *= mask.masks.apod_mask
    if args.ptsrc is not None:
        shape = np.shape(map)
        mask = masks.srcMaskFromfile(args.ptsrc, .25, shape, 0, 
                                     centers[args.field])
    else:
        mask = None
    makeDS9ForBand(args.output, 150, map, [352.5, -55],
                   .25, 0, mask)
        
        
