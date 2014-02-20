from squidSort import squidsort
from sptpol_software.observation.receiver import Receiver
from datetime import datetime, date
import subprocess
import pprint
import pickle, os

rec = Receiver(verbose = False)
pp = pprint.PrettyPrinter(indent = 4)

def getMod(squid_name):
    squid = rec[squid_name]
    b = squid.children[0].id
    b = b.split('.')
    return '.'.join(b[:2])

def countKey(baddies, key):
    tot = len(baddies.keys())
    count = {}
    firsts = {}
    
    for t in sorted(baddies.keys()):
        for s in baddies[t][key]:
            if s not in count.keys():
                firsts[s] = t
                count[s] = 1
            else:
                count[s] += 1

    for s in count.keys():
        count[s] /= float(tot)
        
    return count, firsts

def countMonths():
    datdir = '/data/sptdaq/dfmux/sptpol_receiver_output/BadSquids/'
    for thing in sorted(os.listdir(datdir)):
        if 'squid_history' in thing:
            d = datetime.strptime( thing + '01', 'squid_history_%Y%m.pkl%d')
            if d < datetime(2012, 5, 1):
                continue
            f = open(datdir+thing)
            baddies = pickle.load(f)
            f.close()
            off, offt = countKey(baddies, 'off_squids')
            bad, badt = countKey(baddies, 'bad_squids')
            
            f = open(d.strftime('%b.pkl'), 'w')
            pickle.dump([off, bad], f)
            f.close()


            print d.strftime('== %B ==')
            print '=== Off ==='
            for s in sorted(off.keys(), squidsort):
                if off[s] >= .5 and off[s] < 1.0:
                    print '\t%s %s:  %.3f' %(s, getMod(s), off[s])
                    # print offt[s].strftime('%Y%m%d_%H:%M')
                if off[s] >= 1.0:
                    print '\t%s %s:  ALWAYS' %(s, getMod(s))
            # pp.pprint(off)

            print '=== Bad ==='
            for s in sorted(bad.keys(), squidsort):
                if bad[s] >= .5 and bad[s] < 1.0:
                    print '\t%s %s:  %.3f' %(s, getMod(s), bad[s])
                    # print badt[s].strftime('%Y%m%d_%H:%M')
                if bad[s] >= 1.0:
                    print '\t%s %s:  ALWAYS' %(s, getMod(s))
            # pp.pprint(bad)

def didWeTryToTuneIt(squid, time_str):
    try:
        subprocess.check_call('find /data/sptdaq/dfmux/sptpol_receiver_output/ -path %s* -iname %s*|grep -i %s' %(time_str, squid, squid), shell = True)
    except subprocess.CalledProcessError:
        return False
    return True

if __name__ == '__main__':
    countMonths()

'''

f = open('/data/sptdaq/dfmux/sptpol_receiver_output/BadSquids/squid_history_201211.pkl')
baddies = pickle.load(f)
f.close()

first = True
for i, key in enumerate(baddies.keys()):
    if key < datetime(2012, 11, 20, 23, 03):
        continue
    if first:
        s_off = set(baddies[key]['off_squids'])
        s_bad = set(baddies[key]['bad_squids'])
        first = False
    else:
        s_off.intersection_update(set(baddies[key]['off_squids']))
        s_bad.intersection_update(set(baddies[key]['bad_squids']))

print 'Off squids:'
for s in s_off:
    print '%s:\t %s' %(s, getMod(s))

print 'Bad squids:'
for s in s_bad:
    print '%s:\t %s' %(s, getMod(s))


'''
'''
        self.temporarily_excluded_squids =[# sq7sbpol24 only has resistors.
                                           'Sq7SBpol24', 
                                           # 6/27 NDH
                                           # These squids may be responsible
                                           # for the noise on C4.
                                           # Turned off at Nick Harrington's
                                           # request.
                                           'Sq1SBpol20', 'Sq3SBpol20',
                                           #Turning off Sq5SBpol21 and Sq6...
                                           #because they are noisy bastards
                                           'Sq5SBpol21', 'Sq6SBpol21',
                                           #turning off Because it's noisy and other squids on the wafer have issues
                                           'Sq8SBpol20', #jul19
                                           ]  
'''
