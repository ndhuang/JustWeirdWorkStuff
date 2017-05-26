pro make_sims_cmb, data_dir, nsims = nsims, freq = freq
if n_elements(nsims) eq 0 then nsims = 100
sfreq = strtrim(string(freq, format = '(I03)'),2)
freq_name =  sfreq + 'ghz'

cmbfile='/home/ndhuang/code/clusterFinding/params/ml_l10000_acc2_lensedCls.dat'
readcol, cmbfile, ellraw, dlcmb, junk1, junk2, junk3, /sil
clcmb0 = dlcmb / 1e12 / (ellraw * (ellraw + 1.)) * (2d * !dpi)
clcmb = fltarr(10000)
clcmb[2:9999]=clcmb0[0:9997]
ell = dindgen(n_elements(clcmb))

reso_arcmin = .25
reso = reso_arcmin / 60. / 180. * !dpi

for j = 0, nsims - 1 do begin
   cmbmap = cmb_flatsky(ell, clcmb, 3360, reso)
   save, cmbmap, filename = data_dir + '/field_scaling/sims/cmb' + freq_name + strtrim(j, 2) + '_cmb.sav'
endfor
return
end

pro make_sims_noise, data_dir, njacks, freq
; this is just rewriting the jacks
sfreq = strtrim(string(freq, format = '(I03)'),2)
freq_name =  sfreq + 'ghz'
jack_file = data_dir + '/field_scaling/' + freq_name + '_100_jacks.sav'
print, 'Starting read'
read_jackfile, jack_file, jacks, n1, n2, njacks
for j = 0, njacks - 1 do begin
   print, j
   noisemap = jacks[*, *, j]
   save, noisemap, filename = data_dir + '/field_scaling/sims/noise/' + freq_name + strtrim(j, 2) + '_jack.sav'
   print, j
endfor
return
end

pro make_sims_ptsrc, data_dir, freq, nsims = nsims
if n_elements(nsims) eq 0 then nsims = 100
sfreq = strtrim(string(freq, format = '(I03)'),2)
freq_name =  sfreq + 'ghz'
for j = 0, nsims - 1 do begin
   cr_sim_code_ptsrconly, freq, 3360, 3360, ptsrcmap, 26 * nsims + j
   save, ptsrcmap, filename = data_dir + '/field_scaling/sims/ptsrc/' + freq_name + strtrim(j, 2) + strtrim(j, 2) + '_ptsrc.sav'
endfor
return
end

pro make_sims, data_dir, nsims, freq
  make_sims_noise, data_dir, nsims, freq
end
