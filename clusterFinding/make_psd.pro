pro make_psd,freq,usemem=usemem
field = 'ra23h30dec-55'
sfreq = strtrim(string(freq, format = '(I03)'),2)
freq_name =  sfreq + 'ghz'
;; coadd_dir = '/data39/ndhuang/clusters/ra23h30dec-55/run2/bundles2/'
;; + sfreq + '/'
coadd_dir = '/home/ndhuang/code/clusterFinding/'
psd_file = coadd_dir + 'psd.sav'
psd_fits = coadd_dir + 'psd.fits'
;; mask_file = coadd_dir + 'mask.fits'
mask_file = '/data39/ndhuang/clusters/ra23h30dec-55/run2/bundles2/150/mask.fits'
scrfile = 'none' ; Don't use scratch!
runlist = coadd_dir + 'runlist.txt'
if keyword_set(usemem) then $
  psd = estimate_2d_psd_from_maps_multifield(runlist,apodfile=mask_file,$
                                             freq=freq,$
                                             njacks=100,MAPNAME='MAP',expand_fits=1) $
else $
   stop
   psd = estimate_2d_psd_from_maps_multifield(runlist,apodfile=mask_file,$
                                             scrfile=scrfile,$
                                             freq=freq,filename=psd_file,$
                                             njacks=100,MAPNAME='MAP',expand_fits=1) 
psd_s = {psd: psd}
create_spt_fits_file, psd_fits
add_bintab_to_fits, psd_fits, psd_s, 'psd'
end
