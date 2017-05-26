pro writedbfiles, data_dir, nsims
for isim = 0, nsims - 1 do begin
    outputdir = data_dir + '/field_scaling/clusterfind_sim/run' + strtrim(isim, 2) + '/'
    savefileall = outputdir+'/clusters_allinfo_3-sigma.sav'
    restore, savefileall
    openw, lun, outputdir + '/ClusterCat_twoband_' + strtrim(isim, 2) + '.dat', /get_lun
    nout = n_elements(outtemp_2band)
    os = outtemp_2band
    for i=0,nout-1 do printf, lun, os[i].xpeak, os[i].ypeak, os[i].peaksig, rcvec[os[i].whfilt]
    close, lun
    free_lun, lun
 endfor
end
