import signal, glob, time, os, sys
import time
from datetime import datetime
from multiprocessing import Process, Queue
import numpy as np
import serial
from rs232 import RS232

class Agilent_DMM(RS232):
    def __init__(self, dev, filename, buffer_size = 1024, eol = '\n', 
                 baudrate = 9600, parity = 'N', stopbits = 2, **kwargs):
        self.dev = serial.Serial(dev, baudrate = baudrate, parity = parity, 
                                 stopbits = stopbits, **kwargs)
        self.eol = eol
        self.filename = filename
        self.buffer_size = buffer_size
        # print signal.getsignal(signal.SIGSTOP)
        signal.signal(signal.SIGINT, self.cleanup)
        
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

    def remote(self):
        '''Set the meter in remote mode'''
        self.send(':SYST:REM')
        
    def voltage(self, min, max):
        '''Set up to read a voltage'''
        self.send('CONF:VOLT:DC %f, %f' %(min, max))

    def extTrigger(self):
        '''Set for external triggering'''
        self.send("TRIG:SOUR EXT")

    def intTrigger(self):
        '''Set for internal triggering'''
        self.send("TRIG:SOUR INT")

    def readSingleSample(self):
        '''Read one sample from the dmm'''
        return float(self.readline().strip())

    def listenAndWrite(self, queue):
        '''
        Read many data samples and throw them into a buffer.  Grab the buffer
        and write each one to a file.
        '''
        i = 0
        buff1 = np.zeros(self.buffer_size)
        buff2 = np.zeros(self.buffer_size)
        # self.p = Process(target = self._listen, args = (buff1, buff2, queue))
        # self.p.start()
        self._listen(buff1, buff2, queue)
        while True:
            buff = queue.get(block = True)
            np.save(self.filename + str(i), buff)
            i += 1
            break
        # self.p.join()

    def _listen(self, buff1, buff2, queue):
        i = 0
        while True:
            if i % 2 == 0:
                buff = buff1
            else:
                buff = buff2
            for j in range(self.buffer_size):
                buff[j] = self.readSingleSample()
            queue.put(buff)
            i += 1

if __name__ == '__main__':
    dev = '/dev/ttyUSB2' # find this using dmesg command
    # queue = Queue()
    # data_dir = '/home/sptdaq/Agilent-34401/%s' \
    #     %datetime.utcnow().strftime('%Y%m%d_%H%M')
    # if not os.path.exists(data_dir):
    #     os.makedirs(data_dir)
    # dmm = Agilent_DMM(dev, os.path.join(data_dir, 'data'))
    dmm = Agilent_DMM(dev, '/dev/null')
    dmm.remote()
    f = open(sys.argv[1], 'a')
    # dmm.intTrigger()
    # dmm.voltage(-5, 5)
    # dmm.send("INIT")
    time.sleep(1)
    while True:
        dmm.send("MEAS:VOLT:DC? -10, 10")
        f.write('{}\t{}'.format(time.time(), dmm.readline()))
    # dmm.listenAndWrite(queue)
