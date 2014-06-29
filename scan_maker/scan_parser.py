import numpy as np

class Scan(object):
    def __init__(self, filename):
        data = np.loadtxt(filename, skiprows = 1)
        self.inds = data[:, 0]
        d_az = data[:, 1]
        self.az = np.cumsum(d_az)
        d_el = data[:, 2]
        self.el = np.cumsum(d_el)
        self.flags = data[:, 3]
    
    def double(self):
        self.az = np.concatenate((self.az, self.az))
        self.el = np.concatenate((self.el, self.el))
        self.flags = np.concatenate((self.flags, self.flags))
        self.inds = np.arange(len(self.az))

    def getAzAcc(self, recalc = False):
        if not recalc:
            try:
                return self.az_acc
            except:
                pass
        self.getAzVel()
        self.az_acc = self._differentiate(self.az_vel)
        return self.az_acc
        
    def getAzVel(self, recalc = False):
        if not recalc:
            try:
                return self.az_vel
            except:
                pass
        self.az_vel = self._differentiate(self.az)
        return self.az_vel

    def getElAcc(self, recalc = False):
        if not recalc:
            try:
                return self.el_acc
            except:
                pass
        self.getElVel()
        self.el_acc = self._differentiate(self.el_vel)
        return self.el_acc
        
    def getElVel(self, recalc = False):
        if not recalc:
            try:
                return self.el_vel
            except:
                pass
        self.el_vel = self._differentiate(self.el)
        return self.el_vel

    def _differentiate(self, y, dt = .01):
        return np.diff(np.concatenate(([0], y))) / dt
