from util import GoodVibeBoard

import numpy as np
import pylab as pl

from datetime import datetime, timedelta
from os import path
import gzip
import os, sys
import warnings

class GoodVibeReader(object):
    def __init__(self, start, end, 
                 data_root = '/data/sptdaq/good_vibrations/parser_output/',
                 tick_period = 5.12e-6, ips = ['244', '245', '247'], 
                 verbose = False):
        self.tick_period = tick_period
        self.ips = ips
        self.verbose = verbose
        self.start = start
        self.end = end
        self.root = data_root
        self.read()

    def read(self):
        self.all = []
        for ip in self.ips:
            board = self._read_single(ip)
            if ip == '244':
                self.rxx = board
            elif ip == '245':
                self.rxy = board
            elif ip == '246':
                self.rxz = board
            elif ip == '247':
                self.optics = board
            else:
                warnings.warn('Unkown IP: %s' %ip)


    def _read_single(self, ip):
        datdirs = sorted(os.listdir(self.root))
        dattimes = []
        for d in datdirs:
            try:
                time = datetime.strptime(d, '%Y%m%d_%H%M%S')
                dattimes.append(time)
            except ValueError:
                warnings.warn('Directory %s does not match the time format'
                              %path.join(root, d))

        first = None
        last = None
        for i in range(len(dattimes) - 1):
            if dattimes[i] <= self.start and dattimes[i + 1] > self.start:
                first = i
            elif dattimes[i] < self.end and dattimes[i + 1] >= self.end:
                last = i + 1
                break
        if first is None:
            first = 0
            warnings.warn('Could not find any data for %s.\n' 
                          %self.start.strftime('%Y-%m-%d %H:%M:%S') +
                          'Using %s as the start time instead'
                          %dattimes[first].strftime('%Y-%m-%d %H:%M:%S'))
        if last is None:
            last = len(dattimes) - 1
            warnings.warn('Could not find any data for %s.\n' 
                          %self.end.strftime('%Y-%m-%d %H:%M:%S') +
                          'Using %s as the start time instead'
                          %dattimes[last].strftime('%Y-%m-%d %H:%M:%S'))
        to_read = datdirs[first:last + 1]

        # make a board for each time segment
        boards = []
        for i, d in enumerate(to_read):
            dir = path.join(self.root, d, 'ip' + ip)
            mic = self._read_gzip_file(path.join(dir, 'mic.gz'), 
                                        'mic', 'uint16')
            ticks_mic = self._read_gzip_file(path.join(dir, 'ticks_mic.gz'), 
                                             'ticks_mic', 'int32')
            acc = self._read_gzip_file(path.join(dir, 'accel.gz'),
                                         'acc', 'uint16')
            ticks_acc = self._read_gzip_file(path.join(dir, 'ticks_accel.gz'),
                                                'ticks_acc', 'int32')
            
            mic_t = ticks_mic * self.tick_period
            acc_t = ticks_acc * self.tick_period
            board = GoodVibeBoard(mic, mic_t, acc, acc_t, 
                                  start_time = dattimes[i])
            boards.append(board)

        # join all the time segments, then return the section we were asked for
        board = boards[0].join(boards[1])
        for b in boards[2:]:
            board = board.join(b)
        return board.get_section(self.start, self.end)

    def _read_gzip_file(self, datfile, sensor, dtype):
        self._dbprint('\t reading %s' %sensor)
        try:
            datfile = gzip.open(datfile)
        except IOError, err:
            warnings.warn('Problem opening %s data:\n%s' %(sensor, err))
            return None
        try:
            data = np.fromstring(datfile.read(), dtype = dtype)
        except Exception, err:
            warnings.warn('Problem reading %s data:\n%s' %(sensor, err))
            return None
        datfile.close()
        return data

    def _dbprint(self, msg):
        if self.verbose:
            print msg
