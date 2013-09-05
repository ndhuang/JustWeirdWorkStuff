import numpy as np

def fracDict(fracs, names):
    d = {}
    for f, n in zip(fracs, names):
        if f in d.keys():
            d[f] += [n]
        else:
            d[f] = [n]
    return d

fracs = np.loadtxt('/home/ndhuang/code/auxchecker/bad_elnods.txt', 
                   usecols = (1,))
names = np.loadtxt('/home/ndhuang/code/auxchecker/bad_elnods.txt', 
                   usecols = (0,), dtype = str, delimiter = ', ')
# inds = np.argsort(names)
inds = np.argsort(fracs)
names = names[inds]
fracs = fracs[inds]
del inds
