import serial
class RS232(object):
    def __init__(self, dev, eol = '\r', **kwargs):
        self.dev = serial.Serial(dev, **kwargs)
        self.eol = eol

    def readline(self):
        return self.dev.readline()

    def send(self, msg):
        if not msg.endswith(self.eol):
            msg = msg + self.eol
        self.dev.write(msg)
