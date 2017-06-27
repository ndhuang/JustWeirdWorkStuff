pro clusterfind_sims, data_dir, nsims=nsims, stopit=stopit
if n_elements(nsims) eq 0 then nsims = 100
sim_dir = data_dir + '/field_scaling/sims/'
bands = [90., 150.]
szbands = [91.2, 146.0]
beams = [1.7, 1.14]
reso_arcmin = 0.25
calfac150 = 1.
calfac90 = calfac150
calfacs = [calfac90,calfac150]

nx = 3360
ny = 3360
nside = 3360
maps = dblarr(nx, ny, 3)

; transfer function stuff
; parameters grabbed from cluster finding script
f_hi = .306
f_low = 15.278
isohpf = 400
scanspeed = .275

ellgrid = make_fft_grid(reso_arcmin / 60. * !dtor, nside, nside) * 2 * !pi
f_eff = ellgrid[*, 0] * scanspeed * !dtor / 2 / !pi
good_f = where(f_eff ne 0)
hp1d = fltarr(nside)
hp1d[good_f] = exp(-1. * (f_hi / f_eff[good_f])^6)
hp2d = fltarr(nside, nside)
for i = 0, nside - 1 do hp2d[*, i] = hp1d
lp1d = fltarr(nside)
lp1d[good_f] = exp(-1. * (f_eff[good_f] / f_low)^6)
lp2d = fltarr(nside, nside)
for i = 0, nside - 1 do lp2d[*, i] = lp1d

iso_hp = dblarr(nside, nside) + 1.
good_iso_hp = where(ellgrid lt isohpf)
iso_hp[good_iso_hp] = exp(-(ellgrid[good_iso_hp] - isohpf)^2 / 2. / 20.^2)

beam_trans = fltarr(nside, nside, 2)
transfer_functions = fltarr(nside, nside, 2)
for iband = 0, 1 do begin
    beam_trans[*, *, iband] = (beamfilt(findgen(max(ellgrid) + 1), beams[iband]))[ellgrid]
    transfer_functions[*, *, iband] = beam_trans[*, *, iband] * hp2d[*, *] * lp2d[*, *] * iso_hp[*, *]
endfor

for isim = 0, nsims - 1 do begin
    print, isim
    maps = dblarr(nx, ny, 2)
    szmaps = dblarr(nx, ny, 2)
    restore, sim_dir + '/cmb/ra23h30dec-55_' + strtrim(isim, 2) + '.sav'
    for iband  = 0, 1 do begin
        freq = bands[iband]
        sfreq = strtrim(string(freq, format = '(I03)'),2)
        freq_name =  sfreq + 'ghz'
        restore, sim_dir + '/noise/' + freq_name + strtrim(isim, 2) + '_jack.sav'
        restore, sim_dir + '/ptsrc/ra23h30dec-55_' + strtrim(fix(freq), 2) + '_' + strtrim(isim, 2) + '.sav'
        mask = read_spt_fits(data_dir + '/' + freq_name + '_mask.fits')
        apod_mask = mask.masks.apod_mask
        ; put clusters into center of map
        szmap_small = readfits(sim_dir + '/sz/sz_arnaud_map_' + strtrim(isim, 2) + '.fits')
        szmap = dblarr(nx, ny) * 0
        szmap[nx / 2 - 720:nx / 2 + 719, ny / 2 - 720:ny / 2 + 719] += szmap_small * fxsz(szbands[iband])
        transf = transfer_functions[*, *, iband]
        map = szmap + cmbmap + ptsrcmap
        map_filt = real_part(fft(fft(map * apod_mask) * transf, 1)) / apod_mask
        szmap_filt = real_part(fft(fft(szmap * apod_mask) * transf, 1)) / apod_mask
        good_weight = where(apod_mask gt 1d-6, complement = bad_weight)
        map_filt[bad_weight] = 0d
        szmap_filt[bad_weight] = 0d
        maps[*, *, iband] = map_filt + noisemap
        szmaps[*, *, iband] = szmap_filt
    endfor
    ; setup inputs for clusterfinder
    coadd_file = data_dir + '/field_scaling/temp/coadd_' + strtrim(isim, 2) + '.sav'
    save, maps, filename = coadd_file
    maskfile = data_dir + '/150ghz_mask.fits'
    psdfiles = data_dir + ['/090ghz_', '/150ghz_'] + 'psd.sav'
    radec0 = [352.5, -55.0]
    cmbfile='/home/ndhuang/code/clusterFinding/params/ml_l10000_acc2_lensedCls.dat'
    fileksz = '/home/ndhuang/code/clusterFinding/params/ksz_sehgal.dat'
    profilefile='/home/ndhuang/code/clusterFinding/profiles/profiles_12_beta1_rc025_rc300.sav'
    ptsrc_file = '/home/ndhuang/spt_code/sptpol_software/config_files/ptsrc_config_ra23h30dec-55_surveyclusters.txt'
    ; setup outputs
    outputdir = data_dir + '/field_scaling/clusterfind_sim_120amnoiseband/run' + strtrim(isim, 2) + '/'
    file_mkdir, outputdir
    save, maps, filename = outputdir + '/coadd_' + strtrim(isim, 2) + '.sav'
    savefile = outputdir+'/clusters_3-sigma.sav'
    savefileall = outputdir+'/clusters_allinfo_3-sigma.sav'
    filt_area_file = outputdir + '/filtered_area.sav'
    sz_maps_file = outputdir + '/sz_maps.sav'
    noise1sig=[1e9,1e9,1e9]     ; expect ignored (as of 2015/05/27 it is)
    proj=0
    clusterfind_autotools_nonoise, coadd_file, radec0, maskfile, cmbfile, $
                                   profilefile, ptsrc_file, noise1sig, proj, savefile, $
                                   beams = [1.7, 1.14], psd=psdfiles, savemem=0,$
                                   fileksz=fileksz, savefileall=savefileall,$
                                   hpf=f_hi, lpf = f_low, isohpf = isohpf, $
                                   calfacs=[1., 1.], psmask_arcmin = 4., minrad_ps = 8,$
                                   noise_bandsize_arcmin = 120,$
                                   onlyuse=onlyuse,bands=[90, 150],szbands=szbands, $
                                   filt_area_file = filt_area_file, $
                                   szmaps_file = sz_maps_file, sigmaps = szmaps, /cambcl
    ; make simple text file (for xmatch.pro)
    restore, savefile
    openw, lun, outputdir + '/ClusterCat_twoband_' + strtrim(isim, 2) + '.dat', /get_lun
    nout = n_elements(outtemp_2band)
    os = outtemp_2band
    for i=0,nout-1 do printf, lun, os[i].xpeak, os[i].ypeak, os[i].peaksig, rcvec[os[i].whfilt]
    close, lun
    free_lun, lun
    print, "Found " + strtrim(n_elements(os.xpeak), 1) + " clusters."
    print, "Finished " + strtrim(isim + 1, 2) + ' of ' + strtrim(nsims)
    if keyword_set(stopit) then stop
 endfor
return
end
