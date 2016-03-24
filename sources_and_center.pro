pro sources_and_center, mapfile, maskfile, radec0, reso_arcmin, py_map=py_map, c_map=c_map, fits_map=fits_map
;; grab map
if keyword_set(py_map) then begin 
   map_s = read_spt_hdf5(mapfile, /py_map) 
   map = map_s.map.map
endif else if keyword_set(c_map) then begin
   map_s = read_spt_hdf5(mapfile, /c_map) 
   map = map_s.map.map
endif else if keyword_set(fits_map) then begin
   map_s = read_spt_fits(mapfile)
   map = map_s.coadd.map
endif else begin
   restore, mapfile
   map = maps[*, *, 1]
endelse
mask = read_spt_fits(maskfile)
amask = mask.masks.apod_mask
pmask = mask.masks.pixel_mask
ngrid = n_elements(map[*, 0])

;; find sources.  The noise calculation here might not be the most useful
noise = map_noise(map * amask, reso_arcmin = reso_arcmin) * 1e-6
filt1 = gauss_optfilt(49999L, 1e-6, noise, fwhm_beam = 1.2)
ell_filt = findgen(5e4)
;; use the weighted map from here on
;; good = where(map_s.weight.weight * pmask)
;; map[good] = map[good] / map_s.weight.weight[good]
map_filt = convolve_flatsky(map * amask, reso_arcmin, ell_filt, filt1)
sdtemp = stddev(map_filt[where(pmask)])
atemp = gaussfit_hist(map_filt[where(pmask)], 1000., -5.*sdtemp, 5.*sdtemp)
maprms = atemp[2]
;; maprms = stddev(map_filt * amask)
find_sources_quick, map_filt, os1, maprms = maprms, mapmean = 0., nsigma = 5., reso_arcmin = reso_arcmin, pixel_mask = pmask
pix2ang_proj0, [ngrid, ngrid], radec0, reso_arcmin, ra1, dec1, xp = os1.xpeak, yp = os1.ypeak
;; save, os1, ra1, dec1, file='/data53/ndhuang/ra23h30dec-55/intermediate_20150507/090ghz_ptsrc.sav'
;; return

configfile_out = '/data/ndhuang/test/diff_ptsrc_cat.txt'
save, os1, filename = '/data/ndhuang/test/diff_ptsrc_cat.sav'
ptsrc_output_struct_to_config_file,os1,configfile_out, 'ra23h30dec-55', [ngrid, ngrid],radec0, reso_arcmin, nsigma_min=2.,rad_arcmin_bright=5.,rad_arcmin_dim=2.,nsigma_bright=50.,ra_in=ra1,dec_in=dec1
return

;; print, "ra, dec"
;; for i=0, 2 do begin
;;    print, ra1[i], dec1[i]
;; endfor
;; return

get_pointing_offset_and_rms, map_filt, -1, -1, radec0, 0, os2, reso_arcmin = 0.25, /use_ext, ra_ext = ra1, dec_ext = dec1, sn_ext = os1.peaksig, close_cut_arcsec = 600., /silent
pix2ang_proj0, [ngrid, ngrid], os2.radec0_corr, reso_arcmin, ra2, dec2, xp = os1.xpeak, yp = os1.ypeak
get_pointing_offset_and_rms, map_filt, -1, -1, os2.radec0_corr, 0, pointing_out, reso_arcmin = 0.25, /use_ext, ra_ext = ra2, dec_ext = dec2, sn_ext = os1.peaksig, /silent, nok = nok

if nok eq 0 then return

;; save the output struct in a fits file
basename = strsplit(mapfile, '.', /extract)
basename = basename[0]
outfile = basename + '_pointing.fits'
print, outfile
create_spt_fits_file, outfile
add_bintab_to_fits, outfile, pointing_out, 'pointing'
end
