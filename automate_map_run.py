import string, os, shutil, pickle, sys, glob
import re
from field_centers import centers

output_tag = 'clustermap'
# output_dir = '/mnt/rbfa/ndhuang/maps/clusters/ra3hdec-35/'
log_dir = os.path.join(output_dir, 'logs')
output_dir = '/data53/ndhuang/ra23h30dec-55/T_only'
map_subdir = 'maps'
script_name = os.path.join(output_dir, 'cluster_map_script.sh')
field = 'ra23h30dec-55'
try:
    ra0, dec0 = centers[field]
except KeyError:
    print "I don't have the field center for {!s}, using nominal field center.".format(field)
    match = re.match('ra(\d+)h(\d*)dec([0-9\-]+)', field)
    ra0 = 15 * float(match.group(1))
    if len(match.group(2)) > 0:
        ra0 += float(match.group(2)) / 60 * 15
    dec0 = float(match.group(3))

script_template = string.Template('/home/ndhuang/spt_code/sptpol_cdevel/mapping/scanmap_sim.x -i $input_file -doreal $output_file -n1 8192 -n2 8192 -reso_arcmin 0.25 -ra0 $ra0 -dec0 $dec0 -proj 0 -poly 7 -spatial 0 -nmap 1 -elllpf 20000 -maskedellhpf 400 -o dummy -do_by_wedge -bb_deep_flags -norm_map -is_not_pol -ptsrc $point_source_file 2>&1|tee $log_file')

point_source_file = '/home/ndhuang/spt_code/sptpol_software/config_files/ptsrc_config_5mJy_ra23h30dec-55_20140129_150ghz_withFlux.txt'
# point_source_file = '/home/ndhuang/spt_code/sptpol_software/config_files/ptsrc_config_ra3hdec-35_for_ndh.txt'
stuff_to_do = {'make_script':1,
               'make_maps':  False}

if stuff_to_do['make_script']:
    # done with the configuration
    if not os.path.exists(os.path.join(output_dir, map_subdir)):
        os.makedirs(os.path.join(output_dir, map_subdir))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    shutil.copy(__file__, output_dir)

    # make the script
    input_folder = '/data53/scratch/sptdat/ra23h30dec-55/data/'
    # input_folder = '/mnt/rbfa/ndhuang/auxdata/idf/ra3hdec-35/data'
    input_files = glob.glob(os.path.join(input_folder, '*.h5'))
    regex = re.compile('(ra\d+h\d*dec-\d+)_idf_(\d{8}_\d{6})_(\d{3}ghz)')
    out_str = '#!/bin/bash\n\nulimit -s 32768\n\n'
    for infile in input_files:
        match = re.match(regex, os.path.basename(infile))
        if match is None:
            print "{!s} does not match!".format(os.path.basename(infile))
            continue
        field, date, band = match.groups()
        out_file = os.path.join(output_dir, map_subdir, '_'.join([output_tag, field, date, band]) + '.h5')
        if os.path.exists(out_file):
            continue
        log_file = os.path.join(log_dir, '_'.join([output_tag, field, date, band]) + '.log')
        out_str += 'echo Making %s\n' %out_file
        out_str += script_template.substitute( input_file = infile, output_file = out_file,  point_source_file = point_source_file, log_file = log_file, ra0 = ra0, dec0 = dec0)
        out_str += '\n\n'
    out_str += '\n\n\n'
    f = open(script_name,'w')
    f.write(out_str)
    f.close()
    os.system('chmod u+x %s' % script_name)

if stuff_to_do['make_maps']:
    #run the script
    os.system(script_name)

