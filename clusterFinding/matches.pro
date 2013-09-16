pro matches
cluster_dir='/data39/ndhuang/clusters/ra23h30dec-55/cluster_out/'
sz_dir = 'sptsz/'
data_fitsfile = 'clusters_radec_ra23h30dec-55.fits'
mismatch_file = 'mismatch_inds.bin'
match_file = 'cluster_matches.sav'
magic_sz_file = '/home/ndhuang/code/clusterFinding/sz_clusters.txt'
confirmed_sz_file = '/home/ndhuang/code/clusterFinding/confirmed_sz_clusters.txt'

;; sptsz = read_spt_fits(cluster_dir + sz_dir + data_fitsfile)
restore, cluster_dir + 'clusters_ra23h30dec-55.sav'
sptpol = {out:outtemp_2band}
n_pol = n_elements(sptpol.out.xpeak)
;; convert to ra, dec
;; sz_center = [352.5, -55.0]
;; sz_ra = dblarr(n_sz)
;; sz_dec = dblarr(n_sz)
;; pix2ang_proj0, [3360, 3360], sz_center, .25, sz_ra, sz_dec, xpix = sptsz.out.xpeak, ypix = sptsz.out.ypeak

pol_center = [352.5, -55.0]
pol_ra = dblarr(n_elements(sptpol.out.xpeak))
pol_dec = dblarr(n_elements(sptpol.out.xpeak))
pix2ang_proj0, [4096, 4096], pol_center, .25, pol_ra, pol_dec, xpix = sptpol.out.xpeak, ypix = sptpol.out.ypeak

;; get sz clusters from the magic file
;; readcol, magic_sz_file, junk, sz_ra, sz_dec, sz_sig, format = 'A,D,D,D'
readcol, confirmed_sz_file, name, sz_ra, sz_dec, format = 'A,D,D'
n_sz = n_elements(sz_ra)

wrap = where(sz_ra  lt 180, count)
if count ne 0 then sz_ra[wrap]+=360.
wrap = where(pol_ra lt 180, count)
if count ne 0 then pol_ra[wrap]+=360.

sz_dists = dblarr(n_sz, /nozero)
for i = 0, n_sz - 1 do sz_dists[i] = 600
mismatches = intarr(n_pol)
sz_matches = intarr(n_sz)
polmatch_sig = dblarr(n_pol)
szmatch_sig = dblarr(n_pol)
dists = dblarr(n_pol)
for i=0, n_pol - 1 do begin
   dra = (sz_ra - pol_ra[i]) * cos(pol_dec[i])
   ddec = sz_dec - pol_dec[i]
   distarr = sqrt(dra*dra + ddec*ddec)

   dist = min(distarr, dist_ind)
   dists[i] = dist
   r_core = sptpol.out[i].whfilt * .25 + .25
   if dist gt 2. / 60 then begin
      mismatches[i] = i
   endif else begin
      sz_matches[dist_ind] = 1
      ;; polmatch_sig[i] = sptpol.out[i].peaksig
      ;; szmatch_sig[dist_ind] = sz_sig[dist_ind]
      ;; print, pol_ra[i], ' & ', pol_dec[i], ' & ', r_core, ' & ',
      ;; sptpol.out[i].peaksig, ' & ', sz_sig[dist_ind], ' & ',
      ;; dist*60, '\\'
   endelse
   for j = 0, n_sz - 1 do sz_dists[j] = min([distarr[j], sz_dists[j]])
endfor
nomatch = where(sz_matches eq 0, count)
if count ne 0 then begin
   for i = 0, n_elements(nomatch) - 1 do print, name[nomatch[i]], sz_dists[nomatch[i]]
endif

bad = where(mismatches ne 0, count, complement = good)
if count ne 0 then begin
   cluster_matches = good
   mismatches = bad
endif else cluster_matches = -1
good = where(polmatch_sig ne 0, count)
if count ne 0 then polmatch_sig = polmatch_sig[good]
good = where(szmatch_sig ne 0, count)
if count ne 0 then szmatch_sig = szmatch_sig[good]
save, dists, polmatch_sig, szmatch_sig, mismatches, cluster_matches, filename = cluster_dir + match_file
;; print, '-------------------------------------------------------'
for j=0, n_elements(mismatches) - 1 do begin
   i = mismatches[j]
   r_core = sptpol.out[i].whfilt * .25 + .25
   ;; print, pol_ra[i], ' & ', pol_dec[i], ' & ', r_core, ' & ', sptpol.out[i].peaksig, '\\'
endfor

end
