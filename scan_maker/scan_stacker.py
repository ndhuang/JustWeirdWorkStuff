import numpy as np
from scipy import optimize

def stack(scans, num_scans, wait = 10, rate = 100):
    '''
    Choose a scan length such that scan differences are minimized
    '''
    match_scan = num_scans / 2
    def scanDiff(n):
        n = int(n[0])
        if n * num_scans > len(scans):
            return 1e20
        diffs = np.zeros(n * num_scans)
        match = scans[match_scan * n:(match_scan + 1) * n]
        for i in range(num_scans):
            if i == match_scan:
                # don't try to match a scan with itself
                continue
            diffs[i * n:(i + 1) * n] = match - scans[i * n:(i + 1) * n]
        return sum(diffs**2)
        
    n = len(scans) - wait * rate
    n_scan = n / num_scans # approximate number of points per scan
    n_scan = int(optimize.fmin(scanDiff, n_scan, disp = False)[0])
    
    # stacked = np.zeros(n_scan)
    # for i in range(num_scans):
    #     stacked += scans[i * n_scan:(i + 1) * n_scan]
    stacks = makeStacks(scans, num_scans, n_scan)
    return stacks, n_scan

def makeStacks(scans, num_scans, n_scan):
    stacks = np.zeros((n_scan, num_scans))
    for i in range(num_scans):
        stacks[:, i] = scans[i * n_scan:(i + 1) * n_scan]
    # if np.max(np.std(stacks, 1)) * 3600 > 10:
    #     raise RuntimeError('Stacking didn\'t work very well.  Got max std of %f arcmin!\n' %np.max(np.std(stacks, 1)) * 3600)
    return stacks

def alignScans(scans):
    def scanDiff(cuts):
        diff = 0
        match_scan = scans[-1]
        for i, c in enumerate(cuts):
            # c = int(c)
            # cut_scan = scans[i][c:]
            cut_scan = _makeCut(scans[i], c, len(match_scan))
            diff += sum((cut_scan - match_scan)**2)
        return diff

    guess = np.ones(len(scans) - 1) * 100
    cuts = optimize.fmin(scanDiff, guess, disp = False)
    cut_scans = makeCuts(scans, cuts)
    return cut_scans, cuts

def makeCuts(scans, cuts):
    cut_scans = []
    for i, c in enumerate(cuts):
        cut_scans.append(_makeCut(scans[i], c, len(scans[-1])))
    cut_scans.append(scans[-1])
    return cut_scans
    
def _makeCut(scan, cut, n):
    cut = int(cut)
    if cut > 0:
        cut_scan = scan[cut:]
        # pad!
        cut_scan = np.concatenate((cut_scan, 
                                   np.ones(n - len(cut_scan)) * cut_scan[-1]))
    else:
        # pad the front!
        cut *= -1
        cut_scan = np.concatenate((np.ones(cut) * scan[0], scan))
        cut_scan = cut_scan[:n]
    return cut_scan
    

