pro noise_uk
  bundle_dir = '/data39/ndhuang/clusters/ra23h30dec-55/run2/bundles2/150/bundle*.fits'
  mask_file = '/data39/ndhuang/clusters/ra23h30dec-55/run2/bundles1/150/mask.fits'
  fits_bundles = file_search(bundle_dir)
  weight_map = dblarr(4096, 4096)
  coadd_map = dblarr(4096, 4096)

  for i = 0, n_elements(fits_bundles) - 1 do begin
     map = read_spt_fits(fits_bundles[i])
     if i mod 2 eq 1 then begin
        coadd_map += map.map.map * map.weight.weight
     endif else begin
        coadd_map -= map.map.map * map.weight.weight
     endelse
     weight_map += map.weight.weight
  endfor
  mask = read_spt_fits(mask_file)
  good = where(weight_map gt 0, count, complement = bad)
  if count ne 0 then coadd_map[good] = (coadd_map[good]  / weight_map[good])
  coadd_map[bad] = 0
  coadd_map *= mask.masks.apod_mask
  good = where(coadd_map gt 0)
  print, 'K: ', stddev(coadd_map[good])
  print, 'K-arcmin: ', stddev(coadd_map[good] * .25)
end
