pro noise_uk
  bundle_dir = '/data39/ndhuang/clusters/ra23h30dec-55/run1/bundles/abbys_bundles/bundle*150ghz.fits'
  mask_file = '/data39/ndhuang/clusters/ra23h30dec-55/run1/bundles/abbys_bundles/mask_150ghz.fits'
  fits_bundles = file_search(bundle_dir)
  weight_map = dblarr(4096, 4096)
  coadd_map = dblarr(4096, 4096)

  for i = 0, n_elements(fits_bundles) - 1 do begin
     map = read_spt_fits(fits_bundles[i])
     if i mod 2 eq 1 then begin
        coadd_map[348:348+3399,348:348+3399] += map.map.map * map.weight.weight
     endif else begin
        coadd_map[348:348+3399] -= map.map.map * map.weight.weight
     endelse
     weight_map[348:348+3399,348:348+3399] += map.weight.weight
  endfor
  mask = read_spt_fits(mask_file)
  good = where(weight_map gt 0, count, complement = bad)
  if count ne 0 then coadd_map[good] = (coadd_map[good]  / weight_map[good])
  coadd_map[bad] = 0
  coadd_map *= mask.masks.apod_mask
  save, coadd_map, filename='diffmap_goodweight.sav'
  print, 'uK: ', stddev(coadd_map)
  print, 'uK-arcmin: ', stddev(coadd_map * .25)
end
