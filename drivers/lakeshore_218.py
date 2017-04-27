import argparse
import importlib
import glob
import re
import signal
import time
from multiprocessing import Process, Queue
import numpy as np
import serial
from rs232 import RS232

class Lakeshore_218(RS232):
    '''
    Talk to Lakeshore 218 diode readout boxes.
    '''
    def __init__(self, dev, filename, config_file = None,
                 buffer_size = 128, eol = '\r\n', wait_time = .05,
                 baudrate = 9600, parity = serial.PARITY_ODD, **kwargs):
        '''
        dev: str
            The device node name (typically /dev/ttyS0, or /dev/ttyUSB0, or similar)
        filename: str
            The output filename
        config_file: str
            The config file that provides channel mappings.  Should be in a 
            directory called 'configs' in the working directory.
        buffer_size: int, optional [128]
            The number of samples per channel to store in memory before writing to disk.
            This parameter is a balance between getting data onto disk quickly (for things
            like KST), and IO performance.

        The following parameters are configurations for the serial communication.  
        Probably don't change them.

        eol: str, optional ['\r\n']
        wait_time: float, optional [0.05]
        baudrate: int, optional [9600]
        parity: int, optional [serial.PARITY_ODD]
        '''

        if config_file is None:
            self.channel_names = range(1, 9)
            self.channels = range(1,9)
        else:
            if config_file.endswith('.py'):
                config_file = config_file[:-3]
            config = importlib.import_module('configs.' + config_file, package = 'drivers')
            self.channels = config.channels
            self.channel_names = config.channel_names

        self.dev = serial.Serial(dev, baudrate = baudrate, stopbits = 1,
                                 parity = serial.PARITY_ODD,
                                 bytesize = serial.SEVENBITS, **kwargs)
        self.eol = eol
        self.filename = filename
        self.buffer_size = buffer_size
        self.wait_time = wait_time

    def cleanup(self, signum, frame):
        '''
        Clean up the stub data files.  Combine them into one file.
        '''
        self.dev.close()
        files = glob.glob(self.filename + '*.npy')
        if len(files) != 0:
            data = np.array([np.load(f) for f in files])
            data = data.flatten()
            np.save(self.filename, data)

    def cleanup_simple(self, signum, frame):
        '''
        Clean up the text data files.  Combine them into one file.
        '''
        self.dev.close()
        self.f.close()

    def send(self, msg, wait = True, debug = False):
        '''
        Send a message to the serial device.  If `wait` is set, then wait for 
        `self.wait_time` seconds after sending the message.
        '''
        if not msg.endswith(self.eol):
            msg = msg + self.eol
        if debug:
            print msg
        self.dev.write(msg)
        if wait:
            self.wait()

    def wait(self):
        time.sleep(self.wait_time)

    def find_filenum(self, extension, fail_on_filename = True):
        if not extension.startswith('.'):
            extension = '.' + extension
        files = glob.glob(self.filename + '*' + extension)
        filenum = -1
        pattern = self.filename + '_(\d+)' + extension
        for f in files:
            match = re.match(pattern, f)
            if match is not None:
                filenum = max(filenum, int(match.groups()[0]))
            elif fail_on_filename:
                
                raise RuntimeError("{} does not match filename pattern {}".format(f, pattern))
        return filenum + 1

    def simple_write(self):
        '''
        Unbuffered reading (temps) and writing to file.  Creates a new file
        every ~24 hours.
        '''
        filenum = self.find_filenum('txt')
        self.f = open('{fname}_{fnum:d}.txt'.format(fname = self.filename,
                                                    fnum = filenum), 'w')
        header = sum([[chn + '_time', chn] for chn in self.channel_names], [])
        self.f.write('\t'.join(header))
        self.f.write('\n')
        last = 0
        lines = 0
        last_start = 0
        signal.signal(signal.SIGINT, self.cleanup_simple)
        while True:
            while time.time() - last_start <= .99:
                time.sleep(.01)
            last_start = time.time()
            for i_ch, ch in enumerate(self.channels):
                while time.time() - last < .05:
                    time.sleep(.01)
                val = self.read_single_temp(ch, wait = False)
                t = time.time()
                self.f.write('{:f}\t{:.3f}\t'.format(t, val))
                last = t
            self.f.write('\n')
            lines += 1
            if lines % 10 == 0:
                self.f.flush()
            if lines % 172800 == 0: # ~24 hours
                self.f.close()
                filenum += 1
                self.f = open('{fname}_{fnum:d}.txt'.format(fname = self.filename,
                                                            fnum = filenum), 'w')
                header = sum([[chn + '_time', chn] for chn in self.channel_names], [])
                self.f.write('\t'.join(header))
                self.f.write('\n')
                lines = 0

    def listen_and_write(self, queue):
        '''
        Read many data samples and throw them into a buffer.  Grab the buffer
        and write each one to a file.
        '''
        i = 0
        buff1 = np.zeros((len(self.channels), self.buffer_size, 2))
        buff2 = np.zeros((len(self.channels), self.buffer_size, 2))
        signal.signal(signal.SIGINT, self.cleanup)
        self.p = Process(target = self._listen, args = (buff1, buff2, queue))
        self.p.start()
        while True:
            buff = queue.get(block = True)
            np.save(self.filename + str(i), buff)
            i += 1
        self.p.join()

    def _listen(self, buff1, buff2, queue):
        i = 0
        while True:
            if i % 2 == 0:
                buff = buff1
            else:
                buff = buff2
            for j in range(self.buffer_size):
                for i_ch, ch in enumerate(self.channels):
                    buff[i_ch, j, 0] = time.time()
                    last = buff[i_ch, j, 0]
                    while time.time() - last < .05:
                        time.sleep(.01)
                    buff[i_ch, j, 1] = self.read_single_temp(ch, wait = False)
            queue.put(buff)
            i += 1

    def read_single_temp(self, channel, wait = True):
        if channel > 8 or channel < 1:
            raise ValueError("Channel number must be 1-8, got {}".format(channel))
        self.send('KRDG? {:d}'.format(channel), wait = False)
        val = float(self.readline())
        if wait:
            self.wait()
        return val

    def setup_for_window(self):
        '''
        Configures the box for 2.5V diodes with the generic calibration curve, 
        and turns on display for all channels.
        '''
        for ch in self.channels:
            # Display all channels in order
            self.send('DISPFLD {ch:d},{ch:d},1'.format(ch = ch))
            # Turn all channels on
            self.send('INPUT {ch:d},1'.format(ch = ch))
            # Set all channels to be 2.5 V diodes
            self.send('INTYPE A,0')
            self.send('INTYPE B,0')
            # Set curve
            self.send('INCRV {:d},04'.format(ch))
            self.wait()
        for ch in range(1, 9):
            if ch in self.channels:
                continue
            self.send('INPUT {ch:d},0'.format(ch = ch))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dev', type = str, 
                        help = 'Device name (/deb/ttyUSB0, or similar)')
    parser.add_argument('outfile', type = str, help = 'Output file name')
    parser.add_argument('--config', type = str, help = 'config file name',
                        default = None)
    args = parser.parse_args()
    
    tempmon = Lakeshore_218(args.dev, args.outfile, config_file = args.config)
    tempmon.setup_for_window()
    tempmon.simple_write()
