import os
from sptpol_software.autotools import logs
from sptpol_software.data.readout import SPTDataReader
from sptpol_software.analysis.quicklook import quickmap
from sptpol_software.util.time import SptDatetime
from sptpol_software.analysis.maps import MapAnalyzer
import matplotlib.pyplot as pl

def make_map(start, stop):
    outname = start.strftime('%Y%m%d_%H%M_%0.3dghz.h5')
    if os.path.exists(os.path.join(OUTPUT_DIR, outname %150)):
        # don't repeat work
        pass
    data = SPTDataReader(start_date = start, stop_date = stop,  quiet = True)
    data.readData(start, stop, correct_global_pointing = False, downsample_bolodata = 4)
    ptsrc_file = '/home/ndhuang/spt_code/sptpol_software/config_files/ptsrc_config_ra23h30dec-5520101118_203532.txt'
    map_args = {'good_bolos': ['optical_bolometers',
                              'no_c4',
                              'bolometer_flags',
                              'has_pointing',
                              'has_polcal',
                              'timestream_flags',
                              'elnod',
                              'calibrator',
                              'good_timestream_weight',
                              'full_pixel'],
                'reso_arcmin': 1,
                'proj': 1,
                'map_shape': (25, 70),
                'timestream_filtering': {'poly_order': 1,
                                         'ell_lowpass': 6600},
                'use_c_pointing': False}
    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    print 'Starting mapping'
    _map = quickmap(data, **map_args)
    for band in _map:
        _map[band].writeToHDF5(os.path.join(OUTPUT_DIR, outname %int(band)), overwrite = True)

if __name__ == '__main__':
    # times = [['140326 22:30:51', '140327 01:02:21'], # dither 6
    #          ['140328 10:26:20', '140328 12:57:40'], # dither 12
    #          ['140329 22:28:40', '140330 01:02:44'], # dither 18
    #          ['140331 12:59:38', '140331 15:32:02'], # dither 0
    #          ['140403 07:49:00', 
    #           SptDatetime.now().strftime('%y%m%d %H:%M:%S')]]
    times =[['140525 05:01:19', '140525 07:40:23'], # dither 0
            ['140525 14:16:48', '140525 16:57:01']] # dither 9
    OUTPUT_DIR = '/data/ndhuang/fast_500d_map/run1/proj1'
    datas = []
    for t in times:
        realtimes = logs.readSourceScanTimes(t[0], t[1], 'ra0hdec-57.5', 
                                               nscans_min = 0)
        for rt in realtimes:
            start = SptDatetime(rt[0])
            stop = SptDatetime(rt[1])
            data = SPTDataReader(start_date = start, stop_date = stop, 
                                 quiet = True)
            data.readData(start, stop, correct_global_pointing = False)
            datas.append(data)
            break
            # make_map(start, stop)

    # coadd = sum(maps)
    # ma = MapAnalyzer(delta_ell=25, set_special_bb_bins = False)
    # cls = ma.calculateCls()
    # pl.plot(cls.ell.TT, cls.TT)
    # savefig('/home/ndhuang/plots/ra0hdec-57.5_fast_TT.png')
