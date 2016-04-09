import os
import argparse
from collections import deque
import numpy as np
from spt3g import core, gcp

class Badness(object):
    def __init__(self, n_frames, debug = False):
        self.last_frames = deque([], n_frames)
        self.since_bad = 0
        self.frames_to_keep = n_frames
        self.debug = debug
        self.first = True

    def get_filename(self, fr):
        return fr['antenna0']['tracker']['utc'][0][0].GetFileFormatString() + '_stripped.g3.gz'
    
    def get_newfile(self, fr):
        new_file = self.since_bad > self.frames_to_keep
        if self.debug and new_file:
            print self.get_filename(fr)
        return new_file
        
    def __call__(self, fr):
        if fr.type == core.G3FrameType.EndProcessing:
            return
        fr.type = core.G3FrameType.Timepoint
        self.last_frames.append(fr)
        acu_status = fr['antenna0']['acu']['acu_status'].value
        if acu_status != 224 and acu_status != 192:
            self.first = False
            if self.since_bad < self.frames_to_keep:
                # grab all the frames since the last time we had a bad one
                frames_to_save = list(self.last_frames)[-self.since_bad - 1:]
            else:
                frames_to_save = list(self.last_frames)
            self.since_bad = 0
        else:
            frames_to_save = self.since_bad < self.frames_to_keep and not self.first
            self.since_bad += 1
        return frames_to_save

def print_acu(fr):
    if fr.type == core.G3FrameType.EndProcessing:
        return
    print fr['antenna0']['acu']['acu_status'].value

def time_update(fr):
    if fr.type == core.G3FrameType.EndProcessing:
        return
    if fr['array']['frame']['utc'].time / core.G3Units.s % (60 * 60 * 2) == 0:
        print fr['array']['frame']['utc']

def delete_bolodata(fr):
    if fr.type == core.G3FrameType.EndProcessing:
        return
    fr['receiver_frame'] = fr['receiver']['frame']
    fr.Delete('receiver')

def find_bad(arcfiles, time_gap = 300, 
             directory = '/data31/ndhuang/acu_status_badness',
             debug = False):
    bad_detector = Badness(time_gap, debug)
    pipe = core.G3Pipeline()
    pipe.Add(gcp.ARCFileReader(arcfiles))
    pipe.Add(delete_bolodata)
    pipe.Add(time_update)
    pipe.Add(bad_detector)
    # pipe.Add(print_acu)
    pipe.Add(core.G3MultiFileWriter, 
             filename = lambda fr, seq: os.path.join(directory, bad_detector.get_filename(fr)),
             size_limit = 10 * 1024**3,
             divide_on = bad_detector.get_newfile)
    pipe.Run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action = 'store_true')
    subp = parser.add_subparsers(dest = 'task')
    
    findp =subp.add_parser('find')
    findp.add_argument('arcfiles', nargs = '+')
    findp.add_argument('--time', type = int, default = 300)
    findp.add_argument('--directory', type = str, default = '/data31/ndhuang/acu_status_badness')
    findp.set_defaults(func = find_bad)
    
    args = parser.parse_args()

    if args.task == 'find':
        args.func(args.arcfiles, args.time, args.directory, args.debug)
