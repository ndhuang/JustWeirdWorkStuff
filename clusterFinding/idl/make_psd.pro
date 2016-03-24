pro make_psd, coadd_dir, freq, runlist
sfreq = strtrim(string(freq, format = '(I03)'),2)
freq_name =  sfreq + 'ghz'
;; coadd_dir = '/data39/ndhuang/clusters/ra23h30dec-55/run2/bundles2/'
;; + sfreq + '/'
psd_file = coadd_dir + '/' + freq_name + '_psd.sav'
psd_fits = coadd_dir + '/' + freq_name + '_psd.fits'
;; mask_file = coadd_dir + 'mask.fits'
mask_file = coadd_dir + '/' + freq_name + '_mask.fits'
;; runlist = coadd_dir + '/' + freq_name + '_runlist.txt'
psd = estimate_2d_psd_from_maps_multifield(runlist,apodfile=mask_file,$
                                             freq=freq,$
                                             njacks=100,MAPNAME='MAP',expand_fits=1)
psd_s = {psd: psd}
create_spt_fits_file, psd_fits
add_bintab_to_fits, psd_fits, psd_s, 'psd'
save, psd, filename = psd_file
end
