pro weight_coadd
coadd_output_file = '/data39/ndhuang/clusters/ra23h30dec-55/run1/bundles/abbys_bundles/coadd_150ghz.fits'
coadd_save_file = '/data39/ndhuang/clusters/ra23h30dec-55/run1/bundles/abbys_bundles/coadd.sav'
bundle_dir = '/data39/ndhuang/clusters/ra23h30dec-55/run1/bundles/abbys_bundles/bundle*150ghz.fits'
mask_output_file = '/data39/ndhuang/clusters/ra23h30dec-55/run1/bundles/abbys_bundles/mask_150ghz.fits'
fits_bundles = file_search(bundle_dir)
weight_map = dblarr(3400, 3400)
coadd_map = dblarr(3400, 3400)
for i = 0, n_elements(fits_bundles) - 1 do begin
   map = read_spt_fits(fits_bundles[i])
   coadd_map += map.map.map * map.weight.weight
   weight_map += map.weight.weight

endfor
good=where(weight_map ne 0,complement=bad)
if n_elements(bad) lt 1 then coadd_map(bad)=0
if n_elements(good) lt 1 then begin  
   print, 'Borked!!!!' 
   stop
endif

coadd_map[good] /= weight_map[good]
;; pad!
coadd = dblarr(4096, 4096)
weight = dblarr(4096, 4096)
coadd[348:3399+348,348:3399+348] = coadd_map
weight[348:3399+348,348:3399+348] = weight_map
coadd_struct = {map: coadd, weight: weight, files: fits_bundles}
create_spt_fits_file, coadd_output_file
add_bintab_to_fits, coadd_output_file, coadd_struct, 'coadd'
maps = dblarr(4096, 4096, 2)
maps[*, *, 1] = coadd
save, maps, filename = coadd_save_file
CREATE_APODIZATION_MASKS, weight_map, mask_output_file, threshold=.8
pad_mask, 4096, 4096, mask_output_file
end
