import os, sys
import signal
# import time
from datetime import datetime
# from multiprocessing import Process, Queue
# import numpy as np
import serial
from rs232 import RS232

class Agilent_PS(RS232):
    def __init__(self, dev, filename = None, buffer_size = 1024, eol = '\n', 
                 baudrate = 9600, parity = 'N', stopbits = 2, **kwargs):
        self.dev = serial.Serial(dev, baudrate = baudrate, parity = parity, 
                                 stopbits = stopbits, **kwargs)
        self.eol = eol
        self.filename = filename
        self.buffer_size = buffer_size
        # print signal.getsignal(signal.SIGSTOP)
        # signal.signal(signal.SIGINT, self.cleanup)

    def cleanup(self, signum = None, frame = None):
        '''
        Clean up the text data files.  Combine them into one file.
        '''
        self.dev.close()
        # self.f.close()

    def setVoltage(self, voltage, current = 1, channel = 'P25V',
                   ensure_on = True):
        self.send("APPL {}, {:f}, {:f}".format(channel, voltage, current))
        if ensure_on:
            self.send('OUTP:STATE ON\n')

    def measureOutput(self, channel = 'P25V', verbose = True):
        self.send('MEAS:VOLT? {}'.format(channel))
        out = self.dev.readall().strip()
        volt = float(out)
        self.send('MEAS:CURR? {}'.format(channel))
        out = self.dev.readall().strip()
        curr = float(out)
        if verbose:
            power = abs(curr * volt)
            print datetime.now().strftime("'''%H:%M'''")
            print ': P = {:.03f}    V = {:.03f}    I = {:.03f}'.format(power,
                                                                       volt,
                                                                       curr)
        return volt, curr
        
                  
        
