pro make_psd,freq,usemem=usemem
field = 'ra23h30dec-55'
sfreq = strtrim(string(freq),2) + 'ghz'
coadd_dir = '/data39/ndhuang/clusters/' + field +'/maps/run1/fits/bundles_v0/'
psd_file = coadd_dir + 'psd_' + sfreq + '.sav'
mask_file = coadd_dir + 'mask_' + sfreq + '.fits'
scrfile = 'none' ; Don't use scratch!
runlist = coadd_dir + 'runlist_' + sfreq + '.txt'

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
  

end
