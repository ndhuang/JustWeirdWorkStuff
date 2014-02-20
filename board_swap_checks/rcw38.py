import numpy as np
from sptpol_software.observation.receiver import Receiver
from sptpol_software.util import files

boards = ['120', '122', '144', '150']
rec = Receiver()
bolo_inds = np.zeros(24 * len(boards) * 2, dtype = int)
print np.shape(bolo_inds)
i = 0
for b in boards:
    board = rec.devices.mux_boards[b]
    for squid in board.getSQUIDs():
        squid = board[squid]
        for bolo in squid.getBolosOrderedByFrequency():
            bolo_inds[i] = bolo.index
            i += 1
bolo_inds = bolo_inds[np.nonzero(bolo_inds)[0]]

source_dir = '/data/sptdat/auxdata/source/'
pre_source = 'source_rcw38_20131111_011216.fits'
post_source = 'source_rcw38_20131213_102250.fits'

pre = files.read(source_dir + pre_source)
post = files.read(source_dir + post_source)

deltax = pre.observation.bolo_x_offset - post.observation.bolo_x_offset
deltay = pre.observation.bolo_y_offset - post.observation.bolo_y_offset

