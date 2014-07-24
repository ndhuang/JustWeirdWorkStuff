import cPickle as pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as pl
from sptpol_software.util.time import SptDatetime

def grabKey(stats, key, get_time = False):
    if get_time:
        time = [[] for i in stats]
    min = np.zeros(len(stats.keys()))
    med = np.zeros(len(stats.keys()))
    max = np.zeros(len(stats.keys()))
    for i, cycle_start in enumerate(sorted(stats.keys())):
        if get_time:
            time[i] = SptDatetime(cycle_start)
        min[i], med[i], max[i] = stats[cycle_start][key]
            
    if get_time:
        time = array(time)
        return time, min, med, max
    else:
        return min, med, max

def plotKey(stats, key, hold_time = None, bad_time = 30.0, ridiculous_time = 29.0):
    if hold_time is None:
        hold_time = grabKey(stats, 'hold time', False)
    y = grabKey(stats, key, False)
    baddies = np.where(np.logical_and(hold_time < bad_time,
                                      hold_time > ridiculous_time))[0]
    goodies = np.where(hold_time > bad_time)[0]
    not_ridic = np.concatenate((baddies, goodies))
    pl.figure()
    pl.plot(hold_time[goodies], y[goodies], '.k', label = 'Good Cycles')
    if len(baddies) > 0:
        pl.plot(hold_time[baddies], y[baddies], '.r', label = 'Bad Cycles')
        ymin, ymax = pl.ylim()
        pl.vlines(bad_time, ymin, ymax)
        pl.ylim(ymin, ymax)
    xmin, xmax = pl.xlim()
    pl.hlines(np.median(y[not_ridic]), xmin, xmax, linestyles = 'dashed')
    pl.xlim(xmin, xmax)
    pl.title(key)
    pl.xlabel('Cyle Hold Time (hrs)')
    if 'hold' not in key:
        pl.ylabel('Temperature (K)')
    elif key == 'he4 hold':
        pl.ylabel('He4 Hold Time (minutes)')
    elif key == 'cabin temp':
        pl.ylabel('Cabin Temp (C)')
    elif key == 'wea_airtemp':
        pl.ylabel('Outside Temperature (C)')
    elif key =='wea_winddir':
        pl.ylabel('Wind Direction (grid, degrees)')
    elif key == 'wea_windspeed':
        pl.ylabel('Wind Speed (m/s)')
    pl.legend(loc = 'best')
    pl.savefig('/home/ndhuang/plots/short_cycles/%s.png' 
               %(key.replace(' ', '_')))
    # pl.show()

stats_file = '/home/ndhuang/code/short_cycles/cycle_stats_minmax.pkl'
f = open(stats_file, 'r')
stats = pickle.load(f)
f.close()
# hold_time = grabKey(stats, 'hold time')
# keys = stats[stats.keys()[0]].keys()
# keys.remove('hold time')
# keys = ['cabin temp', 'jack 1']
# for k in keys:
#     plotKey(stats, k, hold_time = hold_time)

if __name__ == '__main__':
    # n = len(stats.keys())
    # he4_hold = np.zeros(n)
    # hex = np.zeros(n)
    # hold = np.zeros(n)
    # ic = np.zeros(n)
    # uc = np.zeros(n)
    # cycle_start = [[] for i in range(n)]

    # for i, k in enumerate(stats):
    #     he4_hold[i] = stats[k]['he4_hold']
    #     hex[i] = stats[k]['hex_med']
    #     ic[i] = stats[k]['ic_med']
    #     uc[i] = stats[k]['uc_med']
    #     hold[i] = stats[k]['hold_time']
    #     cycle_start[i] = SptDatetime(k)

    # cycle_start = np.array(cycle_start)
    pass
