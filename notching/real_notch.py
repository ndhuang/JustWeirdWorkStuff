from datetime import datetime

from sptpol_software.data.readout import SPTDataReader
from sptpol_software.util.time import SptDatetime
from sptpol_software.analysis import processing
from sptpol_software.autotools import logs

for times in logs.readSourceScanTimes('20-Feb-2012', 'now', 'ra23h30dec-55', nscans_min = 1):
    start = SptDatetime(times[0])
    end = SptDatetime(times[1])
    
    try:
        data = SPTDataReader(start, end)
        data.readData()
        processing.notchFilter(data, verbose = True)
    except, err:
        print err
