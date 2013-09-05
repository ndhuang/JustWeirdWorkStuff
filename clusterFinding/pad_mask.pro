pro pad_mask,n1,n2,maskfile
m = read_spt_fits(maskfile)
newap_mask = dblarr(n1, n2)
newpix_mask = dblarr(n1, n2)
newap_mask[0:3399, 0:3399] = m.masks.apod_mask
newpix_mask[0:3399, 0:3399] = m.masks.pixel_mask
newmask = [{masks: {apod_mask: newap_mask, pixel_mask: newpix_mask}}]
write_spt_fits, newmask, maskfile

end
