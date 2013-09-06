pro weight_coadd
coadd_output_file = '/data39/ndhuang/clusters/ra23h30dec-55/bundles/run1/abbys_bundles/coadd_150ghz.idl'
bundle_dir = '/data39/ndhuang/clusters/ra23h30dec-55/bundles/run1/abbys_bundles/bundle*150ghz.fits'
mask_output_file = '/data39/ndhuang/clusters/ra23h30dec-55/bundles/run1/abbys_bundles/mask_150ghz.fits'
fits_bundles = file_search(bundle_dir)
weight_map = dblarr(3400, 3400)
coadd_map = dblarr(3400, 3400)
for i = 0, n_elements(fits_bundles) - 1 do begin
   map = read_spt_fits(fits_bundles[i])
   coadd_map += map.map.map * map.weight.weight
   weight_map += map.weight.weight

endfor
good=where(finite(coadd_map),complement=bad)
if n_elements(bad) lt 1 then coadd_map(bad)=0
if n_elements(good) lt 1 then begin  
   print, 'Borked!!!!' 
   stop
endif

coadd_map[good] /= weight_map[good]
save,fits_bundles,coadd_map,weight_map,filename=coadd_output_file
CREATE_APODIZATION_MASKS, weight_map, mask_output_file, threshold=.8
pad_mask, 4096, 4096, mask_output_file
end
