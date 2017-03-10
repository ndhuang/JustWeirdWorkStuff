#!/bin/bash
DQDIR=/home/ndhuang/code/data_quality/
DQ=dq_plots
DQFANCY=data_quality_`date +%Y%b%d`
DQLINK=/home/ndhuang/current_data_quality.pdf

cd $DQDIR
pdflatex -halt-on-error $DQ.tex > /dev/null
mv $DQ.pdf $DQFANCY.pdf
ln -sf $DQDIR/$DQFANCY.pdf $DQLINK