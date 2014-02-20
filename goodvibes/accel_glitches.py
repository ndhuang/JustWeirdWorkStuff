from gv_datareader import GoodVibeReader

import numpy as np
from datetime import timedelta
import os
import pickle

datdirs = sorted(os.listdir('/data/sptdaq/good_vibrations/parser_output/'))[:-2]

glitches = []
for d in datdirs:
    print d
    data = GoodVibeReader(d)
    for board in data.all:
        glitches += board.find_accel_glitches(9)

glitches = sorted(glitches)
sep = np.diff(glitches)
inds = np.nonzero(sep <= timedelta(seconds = 10*60))[0]
contig = []
i = 0
begin = 0
while i < len(inds) - 1:
    if inds[i + 1] - inds[i] > 1:
        end = i
        contig.append(glitches[int(np.mean([begin, end]))])
        begin = i + 1
    i += 1
    
f = open('accel_glitches.pkl', 'w')
pickle.dump(contig, f)
f.close()
