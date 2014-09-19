#! /bin/bash
function checkCall {
    # check the return value from a command
    cmd=$@
    $cmd
    status=$?
    if [[ status -ne 0 ]]; then
	echo "$cmd failed with exit status $status"
	exit $status
    fi
}

# scripts we need
map_cuts=/home/ndhuang/code/clusterFinding/python/map_cuts.py
idl=/home/ndhuang/code/clusterFinding/idl/cluster_find_field.pro
plot_psd=/home/ndhuang/code/clusterFinding/python/plot_psd.py
ds9=/home/ndhuang/code/clusterFinding/python/make_DS9.py
tex_template=/home/ndhuang/code/clusterFinding/field_clusters.tex

# assume we have maps
# directory structure:
# field_dir/maps contains maps
# data products will be placed in field_dir/
if [[ ${#@} -ne 4 ]]; then
    echo Not the right number of arguments: ${#@}
    echo "Usage:
mega_cluster_script.sh field_dir field ra0 dec0
"
    exit
fi
field_dir=$1
field=$2
ra0=$3
dec0=$4
cluster_dir=$field_dir/cluster_out/new
if [ -e $cluster_dir ]; then
    rm -rf $field_dir/cluster_out/old
    mv $cluster_dir $field_dir/cluster_out/old
fi
plot_dir=$cluster_dir/plots
mkdir -p $plot_dir

main_tex=$cluster_dir/${field}_clusters.tex
# echo $main_tex
# exit
cp $tex_template $main_tex

# first, get statistics and do map cuts
# checkCall python2.7 $map_cuts $field_dir/maps -o $field_dir --tex-file=$main_tex

# now, run the idl crap
echo "\\subsection{Noise per Band}" >> $main_tex
echo "\\begin{tabular}{|l|c|}" >> $main_tex
echo "\\hline" >> $main_tex
echo "Band & Noise (uK-arcmin)\\\\" >> $main_tex
echo "\\hline" >> $main_tex
if [[ $field == 'ra23h30dec-55' ]]; then
    ptsrcfile=$SPTPOL_SOFTWARE/config_files/ptsrc_config_5mJy_ra23h30dec-55_20140129_150ghz_withFlux.txt
else
    ptsrcfile=$SPTPOL_SOFTWARE/config_files/ptsrc_config_{$field}_combined.txt
fi
checkCall idl $idl -args $field_dir $field $ra0 $dec0 $ptsrcfile $main_tex
echo "\\hline" >> $main_tex
echo "\\end{tabular}" >> $main_tex

python2.7 $plot_psd $field_dir --plot-dir $plot_dir --tex-file $main_tex
echo "\\end{document}" >> $main_tex

start_dir=`pwd`
cd $cluster_dir
pdflatex $main_tex > /dev/null
cd $start_dir

python2.7 $ds9 $field --ptsrc $ptsrcfile 