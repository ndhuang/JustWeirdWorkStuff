from sptpol_software.autotools.utils import mkdir_p
from sptpol_software.data.readout import SPTDataReader
from sptpol_software.util.time import SptDatetime
from pylab import *
import sys

sdt = SptDatetime
data = SPTDataReader(master_configfile = 'sptpol_stripped_master_config')
plotdir = '/home/ndhuang/code/test_plots/tracking/'
start = []
end = []
titles = []

# very old lead/trail
titles.append('Very Old L-T')
start.append(sdt('120429 04:05:31'))
end.append(sdt('120429 07:05:31'))

# old lead/trail
titles.append('Old L-T')
start.append(sdt('120521 10:17:19'))
end.append(sdt('120521 13:17:19'))

# old lead/trail
titles.append('Old L-T')
start.append(SptDatetime('120604 16:38:12'))
end.append(SptDatetime('120604 19:38:12'))

# last good lead/trail
titles.append('Last Good L-T')
start.append(SptDatetime('120616 00:08:10'))
end.append(SptDatetime('120616 03:08:10'))

# bad lead/trail
titles.append('Bad L-T')
start.append(SptDatetime('120616 11:13:48'))
end.append(SptDatetime('120616 14:00:48'))

# good lead trail
titles.append('Good L-T amid problems')
start.append(SptDatetime('120618 17:16:46'))
end.append(sdt('120619 02:51:13'))

#=================================================================#

# very old RCW38
titles.append('Very Old RCW38')
start.append(sdt('120429 03:23:37'))
end.append(sdt('120429 04:05:31'))

# old RCW38
titles.append('Old RCW38')
start.append(sdt('120521 04:08:36'))
end.append(sdt('120521 04:50:29'))

# old RCW38
titles.append('Old RCW38')
start.append(SptDatetime('120604 01:57:26'))
end.append(SptDatetime('120604 02:43:26'))

# Normal RCW38 scan
titles.append('Normal RCW38')
start.append(SptDatetime('120614 15:02:02'))
end.append(SptDatetime('120614 15:43:58'))

# The last normal RCW38 scan before tracking problems
titles.append('Last Good RCW38')
start.append(SptDatetime('120615 13:05:37'))
end.append(SptDatetime('120615 13:51:33'))

# RCW38 scan when we got tracking problems
titles.append('Bad RCW38')
start.append(SptDatetime('120616 04:52:27'))
end.append(SptDatetime('120616 05:34:27'))

# RCW38 tracking, no scanning
titles.append('Track RCW38 no scan')
start.append(SptDatetime('120618 14:20:40'))
end.append(SptDatetime('120618 15:03:06'))

# RCW38 tracking, scanning
titles.append('Track RCW38 with scan')
start.append(SptDatetime('120618 15:04:31'))
end.append(SptDatetime('120618 15:19:02'))

# bad RCW38 
titles.append('Bad RCW38')
start.append(sdt('120619 02:51:13'))
end.append(sdt('120619 04:41:36'))

# bad RCW38
titles.append('Bad RCW38')
start.append(sdt('120619 09:00:28'))
end.append(sdt('120619 10:03:11'))

# magical fixed RCW38
titles.append('Good RCW38 (post-reboot)')
start.append(sdt('120619 10:38:26'))
end.append(sdt('120619 11:20:01'))

#=================================================================#

# old cenA
titles.append('Old cenA')
start.append(sdt('120604 02:39:09'))
end.append(sdt('120604 03:14:29'))

# last good cenA
titles.append('Last Good cenA')
start.append(sdt('120615 13:51:33'))
end.append(sdt('120615 14:26:56'))

# magical fixed cenA
titles.append('Good cenA (post reboot)')
start.append(sdt('120619 11:20:21'))
end.append(sdt('120619 11:55:42'))

for t, s, e in zip(titles, start, end):
    if 'L-T' in t:
        outdir = plotdir + 'L-T/'
    elif 'RCW38' in t:
        outdir = plotdir + 'RCW38/'
    elif 'cenA' in t:
        outdir = plotdir + 'cenA/'
    else:
        outdir = plotdir
    mkdir_p(outdir)
    
    t = s.strftime('%m%d %H:%M ') + t
    data.readData(s, e, correct_global_pointing = False, process_psds = False,
                  zero_processing = True)
    time = data.antenna.track_utc
    time = (time - time[0]) * 24 * 60
    elenc1 = data.antenna.track_rawenc[0]
    elenc2 = data.antenna.track_rawenc[1]
    azerr = data.antenna.track_err[0]
    elerr = data.antenna.track_err[1]
    az = data.antenna.track_actual[0]
    el = data.antenna.track_actual[1]

    # tracker errors
    fig = figure(figsize = (12,12))
    
    subplot(211, title = t + ': Az Errors')
    plot(time, azerr)
    ylim(-.05, .05)

    subplot(212, title = t + ': El Errors')
    plot(time, elerr)
    ylim(-.06, .06)

    tight_layout()
    savefig(outdir + t.replace(' ', '_') + '_Errors.png')
    close(fig)

    # actual az/el
    fig = figure(figsize = (12,12))

    subplot(211, title = t + ': Actual Az')
    plot(time, az)

    subplot(212, title = t + ': Actual El')
    plot(time, el)

    tight_layout()
    savefig(outdir + t.replace(' ', '_') + '_Actual.png')
    close(fig)

    # raw encoder
    fig = figure(figsize = (12,12))

    subplot(211, title = t + ': Raw Encoder 1')
    plot(time, elenc1)

    subplot(212, title = t + ': Raw Encoder 2')
    plot(time, elenc2)

    tight_layout()
    savefig(outdir + t.replace(' ', '_') + '_Encoders.png')
    close(fig)
