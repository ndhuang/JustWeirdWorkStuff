pro pad_mask,n1,n2,maskfile
m = read_spt_fits(maskfile)
newap_mask = dblarr(n1, n2)
newpix_mask = dblarr(n1, n2)
newap_mask[0:3399, 0:3399] = m.masks.apod_mask
newpix_mask[0:3399, 0:3399] = m.masks.pixel_mask
newmask = {apod_mask: newap_mask, pixel_mask: newpix_mask}
create_spt_fits_file, maskfile
add_bintab_to_fits,maskfile,newmask,'MASKS'


end
