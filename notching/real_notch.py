from datetime import datetime

from sptpol_software.data.readout import SPTDataReader
from sptpol_software.util.time import SptDatetime
from sptpol_software.analysis import processing
from sptpol_software.autotools import logs
readout_kwargs = {'timestream_units':'Watts', # Convert to T_CMB in preprocessing functions.
                  'correct_global_pointing':True,
                  'downsample_bolodata':4,
                  'project_iq':True,
                  'exception_on_no_iq':True}


for times in logs.readSourceScanTimes('20-Mar-2012', 'now', 'ra23h30dec-55', nscans_min = 1):
    start = SptDatetime(times[0])
    end = SptDatetime(times[1])
    
    try:
        data = SPTDataReader(start, end)
        data.readData(**readout_kwargs)
        processing.notchFilter(data, verbose = True)
    except ValueError, err:
        print err
