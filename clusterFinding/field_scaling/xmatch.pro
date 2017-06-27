pro xmatch, data_dir, nsims
; maximum number of clusters to consider
max_zeta_per_field_per_realization = 300

; create the arrays that will store the sim output
zeta_arr = dblarr(max_zeta_per_field_per_realization, nsims)
ra_arr = dblarr(max_zeta_per_field_per_realization, nsims)
dec_arr = dblarr(max_zeta_per_field_per_realization, nsims)
rcore_arr = dblarr(max_zeta_per_field_per_realization, nsims)
xpix = dblarr(max_zeta_per_field_per_realization, nsims)
ypix = dblarr(max_zeta_per_field_per_realization, nsims)

; these are the map centers for the aardvark+arnaud realizations
nmaps = 18l*18l
ra_cent = reform(rebin(2.5+5.*dindgen(18),18,18), nmaps)
dec_cent = reform(rebin(transpose(2.5+5.*dindgen(18)),18,18), nmaps)
;; in python:
;; reshape(reshape(repeat(arange(18) * 5 + 2.5, 18), (18, 18)).T, 18*18)
nx = 3360
ny = 3360

; grab found clusters
for isim = 0, nsims - 1 do begin
    readcol, data_dir + 'field_scaling/clusterfind_sim_120amnoiseband/run' + strtrim(isim, 2) + '/ClusterCat_twoband_' + strtrim(isim, 2) + '.dat', x, y, zeta, rcore, /sil
    n2p5deg_x = 5 * 60 * 12 * cos(-55 * !dtor) ; approximate number of pixels for 2.5 deg
    n2p5deg_y = 5*60*12                        ; approximate number of pixels for 2.5 degrees
    good_clc = where(zeta gt 0.5 AND $         ; get rid of low significance detections
                     x gt nx/2-n2p5deg_x AND $ ; stay within the simulation region
                     x lt nx/2+n2p5deg_x AND $ ; I'm using a lazy projection (ra*cos(dec0), -dec)
                     y gt ny/2-n2p5deg_y AND $ ; note sanson-flamsteed is ((ra-ra0)*cos(dec), dec-dec0)
                     y lt ny/2+n2p5deg_y $     ; I'm hoping this is ok over only 2.5 degrees
                     , n_good_clc)
    if n_good_clc eq 0 then continue
    
    ; correct for an error in cluster injection
    x = round(x[good_clc]) + 1
    y = round(y[good_clc]) + 1
    ;; NB: it appears that the clusters were injected using proj5,
    ;; onto our proj0 maps.  This should all be fine.
    pix2ang_proj5, [nx, ny], [ra_cent[isim], dec_cent[isim]], 0.25, ra, dec, xpix = x, ypix = y
    unwrap = where(ra gt 180 and ra lt 360, n_unwrap)
    if n_unwrap gt 0 then ra[unwrap] -= 360d

    if max_zeta_per_field_per_realization eq n_good_clc then begin
        rcore_arr[*, isim] = rcore[good_clc]
        zeta_arr[*, isim] = zeta[good_clc]
        ra_arr[*, isim] = ra
        dec_arr[*, isim] = dec
        xpix[*, isim] = x
        ypix[*, isim] = y
    endif else begin
        pad = dblarr(max_zeta_per_field_per_realization - n_good_clc)
        rcore_arr[*, isim] = [rcore[good_clc], pad]
        zeta_arr[*, isim] = [zeta[good_clc], pad]
        ra_arr[*, isim] = [ra, pad]
        dec_arr[*, isim] = [dec, pad]
        xpix[*, isim] = [x, pad]
        ypix[*, isim] = [y, pad]
     endelse
endfor

;; save, zeta_arr, ra_arr, dec_arr, rcore_arr, filename=data_dir + '/field_scaling/xmatch/matched.sav'

; find matches for clusters we put in
cat = mrdfits('/data53/ndhuang/ra23h30dec-55/intermediate_20150507/field_scaling/sims/sz/Aardvark_v0.2_halos.fit', 1)
cat = cat[where(cat.m200 gt 2d14)] ; arnaud only has m200 > 2e14

cluster_inds = where(zeta_arr gt .5, n_clusters)
cat_matcharr = lonarr(n_clusters)
dist_arcsecarr = dblarr(n_clusters)
dra = dblarr(n_clusters)
ddec = dblarr(n_clusters)

for icluster = 0, n_clusters - 1 do begin
    ra = ra_arr[cluster_inds[icluster]]
    dec = dec_arr[cluster_inds[icluster]]
    matches = where(cat.ra gt ra-1 and cat.ra lt ra+1 and $
                    cat.dec gt dec-1 and cat.dec lt dec+1, n_matches)
    if n_matches eq 0 then continue
    ra_rad = ra
    dec_rad = dec 
    gcirc, 2, ra_rad, dec_rad, cat[matches].ra, cat[matches].dec, dist
    dist_arcsecarr[icluster] = min(dist)
    match_ind = matches[(where(dist eq min(dist)))[0]]
    cat_matcharr[icluster] = match_ind
    dra[icluster] = ra - cat[match_ind].ra
    ddec[icluster] = dec - cat[match_ind].dec
endfor
;; save, cat, cat_matcharr, zeta_arr, filename = '/data/ndhuang/test/cluster/xmatch/stuff.sav'

; plots
autohist, dist_arcsecarr, xtitle='nearest N-body halo distance (arcsec)'
window, /free
plot, dist_arcsecarr, zeta_arr[cluster_inds], psym=symcat(16), /xlog, symsize=0.5, ytitle='SZ S/N', xtitle='nearest N-body halo distance (arcsec)'
zeta_arr = zeta_arr[cluster_inds]
masses = cat[cat_matcharr].m200
redshift = cat[cat_matcharr].z
rcore_arr = rcore[cluster_inds]
ra = ra_arr[cluster_inds]
dec = dec_arr[cluster_inds]
matchcat = cat[cat_matcharr]
x = xpix[cluster_inds]
y = ypix[cluster_inds]
save, cluster_inds, zeta_arr, rcore_arr, masses, redshift, dist_arcsecarr, ra, dec, dra, ddec, matchcat, x, y, filename = data_dir + '/field_scaling/xmatch_120amnoiseband/matched_info.sav'

; get a mass-complete catalog
good = where(masses gt 2d14 and redshift gt .3 and dist_arcsecarr lt 65 and zeta_arr gt .5, $
             n_good)
fit_simsr_tdh2, zeta_arr[good], masses[good], redshift[good], pars=pars ; fit a zeta-m relation directly
zetabar = pars[0] * (masses[good] / 3d14)^pars[1] * $
         (Ez(redshift[good]) / Ez(0.6))^pars[2]
resid = zeta_arr[good] / zetabar
zeta_arr = zeta_arr[good]
masses = masses[good]
redshift = redshift[good]
save, zeta_arr, masses, redshift, pars, filename = data_dir + '/field_scaling/xmatch/fit_stuff.sav'

;; get a super robust field scaling factor
fs = median(resid)
print, 'robust field scaling factors:'
print, fs
;; writecol, '~/fsnonoise_xmatched_zeta.txt', fname_arr, fs/0.84 

return
end
