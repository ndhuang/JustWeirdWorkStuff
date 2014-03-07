import numpy as np

from datetime import timedelta

class GoodVibeBoard(object):
    def __init__(self, mic, secs_mic, acc, secs_acc, start_time):
        self.mic = GoodVibeMic(secs_mic, mic)
        self.acc = GoodVibeAcc(secs_acc, acc)
        self.start_time = start_time

    def makeTime(self):
        self.mic.makeTime(self.start_time)
        self.acc.makeTime(self.start_time)


    def getSection(self, start, end):
        start = start.replace(tzinfo = None)
        end = end.replace(tzinfo = None)
        if start < self.start_time:
            raise ValueError('`start` must be after `self.start_time`')
        end_s = end - self.start_time
        end_s = end_s.total_seconds()
        start_s = start - self.start_time
        start_s = start_s.total_seconds()

        mic = self.mic.getSection(start, end)
        acc = self.acc.getSection(start, end)
        return self.fromStreams(mic, acc, start)

    def join(self, other):
        dt = other.start_time - self.start_time
        dt = dt.total_seconds()
        mic = self.mic.join(other.mic, dt)
        acc = self.acc.join(other.acc, dt)
        return self.fromStreams(mic, acc, 
                                min(self.start_time, other.start_time))
    
    @classmethod
    def fromStream(cls, mic, acc, start_time):
        return cls(mic.data, mic.t, acc.data, acc.t, start_time)

    # def split_on_timing(self):
    #     self.mic_sects, self.secs_mic_sects = self._split(self.mic,
    #                                                       self.secs_mic)
    #     self.acc_sects, self.secs_acc_sects = self._split(self.acc,
    #                                                           self.secs_acc)

    # def _split(self, y, t, upper = .0015, lower = .0001):
    #     dt = np.diff(t)
    #     inds = np.nonzero(np.bitwise_or(dt > upper, dt < lower))[0]
    #     sections = []
    #     sections_t = []
    #     last = 0
    #     for i in inds:
    #         section = y[last:i]
    #         section_t = t[last:i]
    #         if len(section) > 1:
    #             sections.append(section)
    #             sections_t.append(section_t)
    #         last = i
    #     return sections, sections_t

class GoodVibeDataStream(object):
    def __init__(self, t, data):
        self.t = t
        self.data = data

    def __call__(self):
        return self.data

    def __getitem__(self, key):
        return GoodVibeDataStream(self.t[key], self.data[key])

    def __iter__(self):
        return self.data.__iter__()

    def makeTime(self, start):
        self.t_obj = np.empty(np.shape(self.t))
        for i in enumerate(self.t):
            dt = timedelta(seconds = self.t[i])
            self.t_obj[i] = start + dt

    def join(self, other, dt):
        if not isinstance(other, type(self)):
            raise TypeError("You shouldn't be combining %s and %s!\n" 
                            %(str(type(self)), str(type(other))) + 
                            "Vaaaat are you sinking?!")
        other.t += dt
        t = np.concatenate([self.t, other.t])
        data = np.concatenate([self.data, other.data])
        
        order = t.argsort()
        t = t[order]
        data = data[order]
        return self.__new__(t, data)

    def getSection(self, start_s, end_s):
        inds = np.nonzero(np.bitwise_and(self.t > start_s, self.t < end_s))
        return self.__new__(self.t[inds], self.data[inds])

class GoodVibeAcc(GoodVibeDataStream):
    def psd(self, **kwargs):
        if 'Fs' in kwargs.keys():
            Fs = kwargs.pop('Fs')
        else:
            Fs = float(len(self.t)) / (self.t[-1] - self.t[0])
        return pl.mlab.psd(self.data, Fs = Fs, **kwargs)

    def findGlitches(self, n_sigma):
        mean = np.mean(self.data)
        std = np.std(self.data)
        inds = np.nonzero(np.array(self.data > mean + n_sigma * std) |
                          np.array(self.data < mean - n_sigma * std))[0]
        times = [self.start_time + timedelta(seconds = t)
                 for t in self.t[inds]]
        return times

class GoodVibeMic(GoodVibeDataStream):
    def psd(self, **kwargs):
        if 'Fs' in kwargs.keys():
            Fs = kwargs.pop('Fs')
        else:
            Fs = float(len(self.t)) / (self.t[-1] - self.t[0])
        return pl.mlab.psd(self.data * self.data, Fs = Fs, **kwargs)
