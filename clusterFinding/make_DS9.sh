#!/bin/bash

fields="ra23hdec-35 ra1hdec-35 ra3hdec-35 ra5hdec-35 ra3hdec-25"
for f in $fields; do
    python2.7 /home/ndhuang/code/clusterFinding/python/make_DS9.py --ptsrc $SPTPOL_SOFTWARE/config_files/ptsrc_config_${f}_combined.txt $f
done