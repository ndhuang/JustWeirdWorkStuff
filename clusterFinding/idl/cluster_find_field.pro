args = command_line_args()
field_dir = args[0]
field = args[1]
radec0 = [args[2], args[3]]
ptsrcfile = args[4]
main_tex = args[5]
texsummary = field_dir + '/cluster_out/new/cluster_summary.tex'
textsummary = field_dir + '/cluster_out/new/' + field + '_3sigma_clusters.txt'
freqs = [90, 150]
npix = [8192, 8192]

i = 0 ; because fuck IDL
print, i
sfreq = strtrim(string(freqs[i], format = '(I03)'))
freq_name =  sfreq + 'ghz'
runlist = field_dir + '/' + freq_name + '_runlist.txt'
weight_coadd, field_dir, runlist, freqs[i]
make_psd, field_dir, freqs[i], /usemem
noise_uk, field_dir, freqs[i], texfile=main_tex

i = 1
print, i
sfreq = strtrim(string(freqs[i], format = '(I03)'))
freq_name =  sfreq + 'ghz'
runlist = field_dir + '/' + freq_name + '_runlist.txt'
weight_coadd, field_dir, runlist, freqs[i]
make_psd, field_dir, freqs[i], /usemem
noise_uk, field_dir, freqs[i], texfile=main_tex

make_clusterlist_catalog_sptpol, field_dir, field, radec0, ptsrcfile
cluster_list_summary, field_dir + 'cluster_out/new/clusters_3-sigma.sav', texsummary, textsummary, radec0, npix, field
exit
