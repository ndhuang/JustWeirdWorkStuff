#!/sptpol_root/bin/python
import cPickle as pickle
import numpy as np
from sptpol_software.data.readout import SPTDataReader
import sptpol_software.util.files as files

def loadDataForAuxFile(aux):
    if isinstance(aux, str):
        aux = files.read(aux)
    data = SPTDataReader(aux.header.start_date, aux.header.stop_date, quiet = True)
    data.readData()
    return data

def quickCheck(auxfiles):
    for f in auxfiles:
        aux = files.read(f)
        try:
            loadDataForAuxFile(aux)
        except KeyError:
            print '\t\t\t' + f

def singleCarrierCheck(data):
    checks = np.zeros((1599,))
    for i,b in enumerate(data.bolodata):
        carrier = data.bolodata[i].readout_settings.carrier_voltage
        not0_carrier = float(len(np.nonzero(carrier)[0]))
        samples = len(data.bolodata[i].readout_settings.carrier_voltage)
        if not0_carrier / samples > .5:
            checks[i] = 1

    return np.mean(checks)

def carrierCheck(auxfiles, carrier_filename, read_filename):
    carrier_out = open(carrier_filename, 'w')
    read_out = open(read_filename, 'w')
    passed_out = open('/home/ndhuang/code/auxchecker/passed_carrier.txt', 'w')
    for af in auxfiles:
        aux = files.read(af)
        try:
            data = loadDataForAuxFile(aux)
        except:
            read_out.write(af + '\n')
            continue
        carrier_frac = singleCarrierCheck(data)
        carrier_out.write(af + ' %f\n' %carrier_frac)
    carrier.close()
    read_out.close()
    passed_out.close()

def carrierComparison(name_dict, carrier_filename, bad_carrier_filename, 
                      other_badness_filename):
    # July 16- this doesn't actually drop anything.  They're all bad
    bad_carrier = open(bad_carrier_filename, 'w')
    other_badness = open(other_badness_filename, 'w')
    carrier_frac_diffs = open('/home/ndhuang/code/auxchecker/carrier_diffs.txt'
                              , 'w')
    auxfiles = np.loadtxt(carrier_filename, usecols = (0,), dtype = str)
    good_carrier_frac = np.loadtxt(carrier_filename, usecols = (1,))
    for af, gf in zip(auxfiles, good_carrier_frac):
        diff = abs(gf - name_dict[af])
        carrier_frac_diffs.write('%s %f\n' %(af, diff))
        if abs(gf - name_dict[af]) > .1:
            other_badness.write('%s %f\n' %(af, gf))
        elif gf < .25:
            bad_carrier.write('%s %f\n' %(af, gf))
    bad_carrier.close()
    other_badness.close()
    carrier_frac_diffs.close()

def readInCheck(bad_readin_filename, error_counts_filename, good_filename,
                error_dict_filename):
    bad_readins = np.loadtxt(bad_readin_filename, usecols = (0,), dtype = str)
    good = open(good_filename, 'w')
    error_count = open(error_counts_filename, 'w')
    error_dict = {}
    for af in bad_readins:
        try:
            loadDataForAuxFile(af)
        except Exception as err:
            err = str(err)
            if err in error_dict.keys():
                error_dict[err] += [af]
            else:
                error_dict[err] = [af]
        else:
            good.write(af + '\n')
                
    for k in error_dict:
        error_count.write('%s: %d\n' %(k, len(error_dict[k])))

    error_file = open(error_dict_filename, 'w')
    pickle.dump(error_dict, error_file)

    error_file.close()
    good.close()
    error_count.close()

if __name__ == '__main__':
    # from loadup import *
    # # inds = np.where((fracs > .01))
    # carrierCheck(names, '/home/ndhuang/code/auxchecker/carrier.txt', 
    #              '/home/ndhuang/code/auxchecker/bad_readin.txt')
    # good_frac = np.loadtxt('/home/ndhuang/code/auxchecker/bad_elnods.txt', 
    #                        usecols = (1,))
    # auxfiles = np.loadtxt('/home/ndhuang/code/auxchecker/bad_elnods.txt', 
    #                       usecols = (0,), dtype = str, delimiter = ', ')
    # name_dict = {}
    # for af, gf in zip(auxfiles, good_frac):
    #     name_dict[af] = gf

    # carrierComparison(name_dict, '/home/ndhuang/code/auxchecker/carrier.txt', 
    #                   '/home/ndhuang/code/auxchecker/bad_carrier.txt', 
    #                   '/home/ndhuang/code/auxchecker/not_carrier_bad.txt')
    readInCheck('/home/ndhuang/code/auxchecker/bad_readin.txt', 
                '/home/ndhuang/code/auxchecker/readin_error_counts.txt',
                '/home/ndhuang/code/auxchecker/magically_saved_readin.txt',
                '/home/ndhuang/code/auxchecker/readin_error.pkl') 
