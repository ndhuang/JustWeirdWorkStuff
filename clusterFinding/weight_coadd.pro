pro weight_coadd, input_dir, output_dir, freq
sfreq = strtrim(string(freq, format = '(I03)'))
coadd_fits_file = output_dir + '/' + sfreq + '/coadd.fits'
coadd_save_file = output_dir + '/coadd.sav'
bundle_dir = input_dir + '/' + sfreq + '/bundle*.fits'
mask_output_file = output_dir + '/' + sfreq + '/mask.fits'
fits_bundles = file_search(bundle_dir)
weight = dblarr(4096, 4096)
coadd = dblarr(4096, 4096)
for i = 0, n_elements(fits_bundles) - 1 do begin
   map = read_spt_fits(fits_bundles[i])
   coadd += map.map.map * map.weight.weight
   weight += map.weight.weight

endfor
good=where(weight ne 0,complement=bad)
if n_elements(bad) lt 1 then coadd(bad)=0
if n_elements(good) lt 1 then begin  
   print, 'Borked!!!!' 
   stop
endif

coadd[good] /= weight[good]

coadd_struct = {map: coadd, weight: weight, files: fits_bundles}
create_spt_fits_file, coadd_fits_file
add_bintab_to_fits, coadd_fits_file, coadd_struct, 'coadd'

;; if the coadd save file exists, restore it and overwrite with new data
if file_test(coadd_save_file) eq 1 then restore, coadd_save_file $
else maps = dblarr(4096, 4096, 2)

if freq eq 90 then maps[*, *, 0] =coadd $
else maps[*, *, 1] = coadd
save, maps, filename = coadd_save_file
CREATE_APODIZATION_MASKS, weight, mask_output_file, threshold=.8
end
