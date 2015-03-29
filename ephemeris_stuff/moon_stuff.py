import argparse
from datetime import timedelta, datetime
import numpy as np
import ephem
import spt
spt = spt.getSPT()

def _getMoonPos(observer, pole = True):
    moon = ephem.Moon(observer)
    if pole:
        return np.asarray([moon.az + np.deg2rad(float(observer.lon)), moon.alt, moon.moon_phase])
    else:
        return np.asarray([moon.az, moon.alt, moon.moon_phase])

def getMoonPos(observer, start, stop, pole = True):
    duration = int(np.ceil((stop - start).total_seconds() / 1800))
    times = np.asarray([start] * duration)
    az = np.zeros(duration)
    el = np.zeros(duration)
    phase = np.zeros(duration)
    for i in range(duration):
        times[i] += timedelta(hours = i * .5)
        observer.date = times[i]
        az[i], el[i], phase[i],  = _getMoonPos(observer, pole)
    return times, np.rad2deg(az), np.rad2deg(el), phase

def NOAA(year, outfile):
    start = datetime(year, 3, 1, 0)
    stop = datetime(year, 10, 1, 0)
    time, az, el, phase = getMoonPos(spt, start, stop)
    good = np.where((az > 50) & (az < 260) & (el > 10))[0]
    diffs = np.diff(good)
    transitions = np.where(diffs > 1)[0]
    transitions = good[transitions]
    f = open(outfile, 'w')
    f.write("date\ttime\tazimuth\televation\tphase\n")
    for i in transitions:
        f.write("{date}\t{time}\t{az}\t{el}\t{phase}\n".format(date = time[i].strftime("%Y-%m-%d"), time = time[i].strftime("%H:%M:%S"), az = az[i], el = el[i], phase = phase[i]))
    f.close()

if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--noaa')
    for year in np.arange(9) + 2015:
        NOAA(year, "{:d}_moon.tsv".format(year))
    
