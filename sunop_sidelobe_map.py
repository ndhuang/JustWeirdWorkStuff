import os, sys
import glob
from multiprocessing import Pool
from datetime import timedelta
import numpy as np
import matplotlib.pyplot as pl
from sptpol_software.util import files
from sptpol_software.autotools import logs
from sptpol_software.data.readout import SPTDataReader
from sptpol_software.analysis.quicklook import quickmap
from sptpol_software.analysis.c_mapper import cMapping
from sptpol_software.data.mapidf import MapIDF
from sptpol_software.util.time import SptDatetime
from sptpol_software.analysis import cuts

def make_idf(interval, ok_time):
    start = interval[0]
    stop = interval[1]
    # if os.path.exists(os.path.join(OUTPUT_DIR, 'left', outname %150)):
    #     return None
    # try:
    #     os.makedirs(os.path.join(OUTPUT_DIR, 'left'))
    #     os.makedirs(os.path.join(OUTPUT_DIR, 'right'))
    # except OSError:
    #     pass
    inter_time = start + ok_time
    idf_num = 0
    while inter_time < stop:
        # data = SPTDataReader(inter_time - ok_time, inter_time, verbose = True)
        # data.readData(correct_global_pointing = False, downsample_bolodata = 8, timestream_units = 'power')
        # idf150 = MapIDF(data, freq = 150)
        # idf150.writeToHDF5(os.path.join(OUTPUT_DIR, 'idf_150ghz_{:02d}.h5'.format(idf_num)), 
        #                    as_stub = False, overwrite = True)
        # idf090 = MapIDF(data, freq = 90)
        # idf090.writeToHDF5(os.path.join(OUTPUT_DIR, 'idf_090ghz_{:02d}.h5'.format(idf_num)), 
        #                    as_stub = False, overwrite = True)
        idf_num += 1
        inter_time += ok_time
    data = SPTDataReader(inter_time - ok_time, stop, verbose = True)
    data.readData(correct_global_pointing = False, downsample_bolodata = 8, timestream_units = 'power')
    idf150 = MapIDF(data, freq = 150)
    idf150.writeToHDF5(os.path.join(OUTPUT_DIR, 
                                    'idf_150ghz_{:02d}.h5'.format(idf_num)), 
                       as_stub = False, overwrite = True)
    idf090 = MapIDF(data, freq = 90)
    idf090.writeToHDF5(os.path.join(OUTPUT_DIR, 
                                    'idf_090ghz_{:02d}.h5'.format(idf_num)), 
                       as_stub = False, overwrite = True)
    return

def make_idf_pieces(start, stop):
    intervals = [[start, '03-Feb-2015:06:21:41'],
                 ['03-Feb-2015:06:21:48', '03-Feb-2015:08:20:37'],
                 ['03-Feb-2015:08:20:44', '03-Feb-2015:10:20:44'],
                 ['03-Feb-2015:10:20:53', stop]]
    idf_num = 0
    for start, stop in intervals:
        data = SPTDataReader(start, stop, verbose = True)
        data.readData(correct_global_pointing = False, downsample_bolodata = 8, timestream_units = 'power', verbose = True)
        idf150 = MapIDF(data, freq = 150)
        idf150.writeToHDF5(os.path.join(OUTPUT_DIR, 
                                        'idf_150ghz_{:02d}.h5'.format(idf_num)), 
                           as_stub = False, overwrite = True)
        idf090 = MapIDF(data, freq = 90)
        idf090.writeToHDF5(os.path.join(OUTPUT_DIR, 
                                        'idf_090ghz_{:02d}.h5'.format(idf_num)), 
                           as_stub = False, overwrite = True)
        idf_num += 1
    return
        
'''
    ptsrc_file = '/home/ndhuang/spt_code/sptpol_software/config_files/ptsrc_config_ra23h30dec-5520101118_203532.txt'
    map_args = {'good_bolos': ['optical_bolometers',
                              'no_c4',
                              'bolometer_flags',
                              'has_pointing',
                              'has_polcal',
                              'timestream_flags',
                              # 'elnod',
                              # 'calibrator',
                              'good_timestream_weight',],
                'reso_arcmin': 30,
                'proj': 1,
                'map_shape': (45, 170),
                'map_center': [9 * 15, -51],
                'timestream_filtering': {'poly_order': 0,}}
                                         # 'ell_lowpass': 360,
                                         # 'ell_highpass': 10},}
                # 'doreal': True}
    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    print 'Starting mapping'
    left_map = cMapping(data, use_leftgoing = True, doreal = True, **map_args)
    right_map = cMapping(data, use_leftgoing = False, doreal = True, **map_args)
    # left_map = quickmap(data, use_leftgoing = True, **map_args)
    # right_map = quickmap(data, use_leftgoing = False, **map_args)
    for band in left_map:
        left_map[band].writeToHDF5(os.path.join(OUTPUT_DIR, 'left', outname %int(band)), overwrite = True)
    for band in right_map:
        right_map[band].writeToHDF5(os.path.join(OUTPUT_DIR, 'right', outname %int(band)), overwrite = True)
    return None
'''
def make_time(interval):
    return [SptDatetime(interval[0]), SptDatetime(interval[1])]

def idf_to_map_half(outdir):
    try:
        os.makedirs(os.path.join(outdir, 'left'))
        os.makedirs(os.path.join(outdir, 'right'))
    except OSError:
        pass
    map_args = {'good_bolos': ['optical_bolometers',
                              'no_c4',
                              'bolometer_flags',
                              'has_pointing',
                              'has_polcal',
                              'timestream_flags',
                              # 'elnod',
                              # 'calibrator',
                              'good_timestream_weight',],
                'reso_arcmin': 30,
                'proj': 1,
                'map_shape': (45, 170),
                'map_center': [9 * 15, -51],
                'timestream_filtering': {'poly_order': 0,}}
    bands = [90, 150]
    dirs = ['half1', 'half2']
    for b in bands:
        idfs = []
        for d in dirs:
            idfs.append(files.read(glob.glob(os.path.join(outdir, d, '*{:03d}*.h5'.format(b))))[0])
        maps_left = [cMapping(i, doreal = True, use_leftgoing = True,
                              **map_args)[str(b)] for i in idfs]
        maps_right = [cMapping(i, doreal = True, use_leftgoing = False,
                               **map_args)[str(b)] for i in idfs]
        left = np.sum(maps_left)
        right = np.sum(maps_right)
        left.writeToHDF5(os.path.join(outdir, 'left', 
                                      'sunop_map_{:03d}ghz.h5'.format(b)),
                         overwrite = True)
        right.writeToHDF5(os.path.join(outdir, 'right', 
                                       'sunop_map_{:03d}ghz.h5'.format(b)),
                         overwrite = True)
    return left, right

def map_from_many_idfs(idf_list, outdir):
    map_args = {'good_bolos': ['optical_bolometers',
                              'no_c4',
                              'bolometer_flags',
                              'has_pointing',
                              'has_polcal',
                              'timestream_flags',
                              # 'elnod',
                              # 'calibrator',
                              'good_timestream_weight',],
                'reso_arcmin': 30,
                'proj': 1,
                'map_shape': (45, 170),
                'map_center': [9 * 15, -51],
                'timestream_filtering': {'poly_order': 4,
                                         'ell_lowpass': 360}}    
    glitchfinder_args = {'timestream_ids_to_check':None, 
                         'ps_list':"",
                         'verbose':True}
    cutter = cuts.Cutter()
    idfs = []
    for i_file in idf_list:
        idf = files.read(i_file)
        cutter.flagTimestreamJumps(idf, **glitchfinder_args)
        idfs.append(idf)
    maps_left = [cMapping(i, doreal = True, use_leftgoing = True,
                              **map_args)[str(idfs[0].band)] for i in idfs]
    maps_right = [cMapping(i, doreal = True, use_leftgoing = False,
                              **map_args)[str(idfs[0].band)] for i in idfs]
    left = np.sum(maps_left)
    right = np.sum(maps_right)
    left.writeToHDF5(os.path.join(outdir, 'left', 
                                  'sunop_map_{:03d}ghz.h5'.format(idfs[0].band)),
                     overwrite = True)
    right.writeToHDF5(os.path.join(outdir, 'right', 
                                   'sunop_map_{:03d}ghz.h5'.format(idfs[0].band)),
                      overwrite = True)
    return left, right

if __name__ == '__main__':
    N_PROCS = 4
    OUTPUT_DIR = '/data/ndhuang/sunop_sidelobe'

    realtimes = logs.readSourceScanTimes('20150201', '20150205', 
                                         'opsun', nscans_min = 0)
    # make_idf_pieces(realtimes[0][0], realtimes[0][1])
    
    idf90 = glob.glob(os.path.join(OUTPUT_DIR, 'idf*090ghz*.h5'))
    map_from_many_idfs(idf90, OUTPUT_DIR)
    idf150 = glob.glob(os.path.join(OUTPUT_DIR, 'idf*150ghz*.h5'))
    map_from_many_idfs(idf150, OUTPUT_DIR)
