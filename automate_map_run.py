import string, os, shutil, pickle, sys, glob


output_tag = 'clustermap_'
output_dir = '/mnt/rbfa/ndhuang/maps/clusters/ra3hdec-25/'
map_subdir = 'maps'
script_name = os.path.join(output_dir, 'cluster_map_script.sh')

script_template = string.Template('/home/ndhuang/spt_code/sptpol_cdevel/mapping/scanmap_sim.x -i $input_file -doreal $output_file -n1 4096 -n2 4096 -reso_arcmin 0.25 -ra0 352.515 -dec0 -55 -proj 0 -poly 7 -spatial 0 -nmap 1 -elllpf 20000 -maskedellhpf 400 -o dummy -do_by_wedge -inv_bolo_flags has_pointing,has_polcal -ignore_bolo_flags has_time_const,good_angle_fit,good_xpol_fit -ptsrc $point_source_file \n')

point_source_file = '/home/ndhuang/spt_code/sptpol_software/config_files/ptsrc_config_5mJy_ra23h30dec-55_20140129_150ghz_withFlux.txt'
stuff_to_do = {'make_script':1,
               'make_maps':  False}

if stuff_to_do['make_script']:
    # done with the configuration
    if not os.path.exists(os.path.join(output_dir, map_subdir)):
        os.makedirs(os.path.join(output_dir, map_subdir))
    shutil.copy(__file__, output_dir)

    # make the script
    input_folder = '/data53/scratch/sptdat/ra23h30dec-55/data/'
    input_files = glob.glob(os.path.join(input_folder, '*.h5'))
    map_names = [os.path.basename(in_file).split('.')[0] for in_file in input_files]
    map_names = ['_'.join(mn.split('_idf_')) for mn in map_names]
    output_files = [os.path.join(output_dir, map_subdir, output_tag + map_name + '.h5') for map_name in map_names]
    out_str = '#!/bin/bash\n\nulimit -s 32768\n\n'

    for in_file, out_file in zip(input_files,output_files):
        out_str += 'echo Making %s\n\n' %out_file
        out_str += script_template.substitute( input_file = in_file, output_file = out_file,  point_source_file = point_source_file)

    out_str += '\n\n\n'
    f = open(script_name,'w')
    f.write(out_str)
    f.close()
    os.system('chmod u+x %s' % script_name)

if stuff_to_do['make_maps']:
    #run the script
    os.system(script_name)

