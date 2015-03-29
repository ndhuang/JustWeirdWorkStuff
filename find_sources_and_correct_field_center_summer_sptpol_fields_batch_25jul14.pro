;; read in an sptpol summer-field 150 GHz map and weights, make apod
;; mask, point-source filter, find sources, see if field center needs
;; to be corrected, the write source files.
;
;thisfield = 'ra23hdec-35'
;tcdir = '/data/tcrawfor/sptpol_maps/T_maps_ndhuang_clusters/summer_fields/'
;thisdir = tcdir + thisfield + '/'
;
;mstemp = read_spt_fits(thisdir+'150ghz_coadd.fits')
;map = mstemp.coadd.map
;weights = mstemp.coadd.weight
;maskfile = thisdir + 'masks_150_0p8.fits'
;maskcheck = file_search(maskfile,count=nmf)
;if nmf eq 0 then begin
;    create_apodization_masks,weights,maskfile,thresh=0.8
;endif
;maskstr = read_spt_fits(maskfile)
;apod = maskstr.masks.apod_mask
;pmask = maskstr.masks.pixel_mask
;
field = 'ra3hdec-25'
field_dir = '/mnt/rbfa/ndhuang/maps/clusters/' + field + '/'
;; mask = read_spt_fits(field_dir + '150ghz_mask.fits')
mask = read_spt_fits('/data/ndhuang/test/mask.fits')
apod = mask.masks.apod_mask
pmask = mask.masks.pixel_mask
coadd = read_spt_hdf5('/data/ndhuang/test/coadd.h5')
;; mstruct = read_spt_fits(field_dir + 'coadd.fits')
;; map = mstruct.coadd.map
;; weight = mstruct.coadd.weight
;; restore, field_dir + 'coadd.sav'
;; map = maps[*, *, 1]
map = coadd.map
ngrid = n_elements(map[*,0])
reso_arcmin = 0.25
if field eq 'ra23hdec-35' then radec0 = [345.02928, -35.02945]
if field eq 'ra1hdec-35' then radec0 = [15.02715,-35.03219]
if field eq 'ra3hdec-35' then radec0 = [45.02797,-35.02987]
if field eq 'ra5hdec-35' then radec0 = [75.01397,-35.01137]
if field eq 'ra3hdec-25' then radec0 = [45.01047,-25.04558]

filt1 = gauss_optfilt(49999L,1e-6,30e-6,fwhm_beam=1.2)
ell_filt = findgen(5e4)
map_filt = convolve_flatsky(map*apod,reso_arcmin,ell_filt,filt1)
stop
sdtemp = stddev(map_filt[where(pmask)])
atemp = gaussfit_hist(map_filt[where(pmask)],1000.,-5.*sdtemp,5.*sdtemp,/plot)
stop
maprms = atemp[2]
stop
find_sources_quick,map_filt,os1,maprms=maprms,mapmean=0.,nsigma=5.,reso_arcmin=0.25,pixel_mask=pmask

pix2ang_proj0,[ngrid,ngrid],radec0,reso_arcmin,ra1,dec1,xp=os1.xpeak,yp=os1.ypeak
get_pointing_offset_and_rms,map_filt,-1,-1,radec0,0,os2,reso_arcmin=0.25,/use_ext,ra_ext=ra1,dec_ext=dec1,sn_ext=os1.peaksig,close_cut_arcsec=600.
pix2ang_proj0,[ngrid,ngrid],os2.radec0_corr,reso_arcmin,ra2,dec2,xp=os1.xpeak,yp=os1.ypeak
get_pointing_offset_and_rms,map_filt,-1,-1,os2.radec0_corr,0,os3,reso_arcmin=0.25,/use_ext,ra_ext=ra2,dec_ext=dec2,sn_ext=os1.peaksig
radec0_orig = radec0
radec0 = os3.radec0_corr
pix2ang_proj0,[ngrid,ngrid],os3.radec0_corr,reso_arcmin,ra3,dec3,xp=os1.xpeak,yp=os1.ypeak

configfile_out = '/home/ndhuang/spt_code/sptpol_software/config_files/ptsrc_config_'+field+'_for_ndh.txt'
ptsrc_output_struct_to_config_file,os1,configfile_out,field,-1,-1,-1,nsigma_min=5.,rad_arcmin_bright=5.,rad_arcmin_dim=2.,nsigma_bright=50.,ra_in=ra3,dec_in=dec3
