import numpy as np
from matplotlib import pyplot as pl
from sptpol_software.autotools import logs
import sptPyReadArc as arc

# read in data
start, stop = logs.readSourceScanTimes('20150201', '20150204', 
                                       'opsun', nscans_min = 10)[0]
# First, read in the entire with one bolo
data_small = arc.readArc(['receiver.bolometers.adcCountsI[0]~ double',
                          'antenna0.tracker.scan_flag~ uint'], 
                         str(start), str(stop), 
                         '/data/sptdat/arcfile_directory/20150129_000000/')
# Now, the full set (~60 GB)
data_full = arc.readArc(['receiver.bolometers.adcCountsI[0-1599]~ double',
                         'antenna0.tracker.scan_flag~ uint'],
                        str(start), str(stop),
                        '/data/sptdat/arcfile_directory/20150129_000000/')

# Upsample the scan flags
# I have tested that the scan flags are identical between data_full and 
# data_small, but you can test this:
# np.nonzero(data_small['antenna0.tracker.scan_flag'][0] - 
#            data_full['antenna0.tracker.scan_flag'][0])

# I am assuming that the scan flags and bolodata vectors cover exactly the 
# same amount of time so I can use the index as a proxy for time.
# Since this works with the small data sample, I believe the assumptions
# are correct
inds_slow = np.arange(len(data_small['antenna0.tracker.scan_flag'][0]),
                      dtype = np.uint)
inds_interp = np.linspace(0, len(inds_slow), 
                          len(data_small['receiver.bolometers.adcCountsI'][0]))
fast_scan_flags = np.interp(inds_interp, inds_slow, 
                            data_small['antenna0.tracker.scan_flag'][0])
# this gives us something that gradually moves from 0 to 1 at the transitions.
# scan flags are binary, so force them to be ints
fast_scan_flags = fast_scan_flags.astype(np.uint)
# This means we can't trust one or two of the flags near the transition,
# but that doesn't really matter here.  We're looking at offsets of 15s.

# Now, let's take all the indices where the scan flags are 0 
# these are the turnarounds
turns = np.nonzero(fast_scan_flags - 1)[0]

# Now, zero the bolo data in the turnarounds
data_small['receiver.bolometers.adcCountsI'][:, turns] = 0
data_full['receiver.bolometers.adcCountsI'][:, turns] = 0

# In principle, we should have real data in the valid portion of the scan
# (neglecting any sort of wobble), and zeros elsewhere.
# Let's make some plots

fig = pl.figure()
ax1 = pl.subplot(211)
# This should look good- no big jumps in the bolodata
pl.plot(data_small['receiver.bolometers.adcCountsI'][0])
pl.ylim(3.85e7, 3.9e7 + 2245127)
pl.subplot(212, sharex = ax1)
# This should have large jumps in alternate scans- these are the el steps
# There should also be a large DC jump at the end.  As it turns out, the
# data after the DC jump perfectly matches the single bolo read.  The data
# before the jump is wrong.  Just subtract the registers, and you'll see it.
pl.plot(data_full['receiver.bolometers.adcCountsI'][0])
pl.ylim((80979883, 83225010))
pl.xlim((800208, 869662))
pl.savefig('scanoffsets.png')
