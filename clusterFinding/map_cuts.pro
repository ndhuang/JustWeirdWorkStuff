pro map_cuts, directory, junkfile=junkfile, weight_thresh=weight_thresh
  if n_elements(junkfile) lt 1 then junkfile = '/data/ndhuang/mapcutjunk.fits'
  if n_elements(weight_thresh) lt 1 then weight_thresh = .3
  mapfiles = file_search(directory + '*150ghz.h5')
  nmaps = n_elements(mapfiles)
  rms = dblarr(nmaps)
  med_weight = dblarr(nmaps)
  tot_weight = dblarr(nmaps)
  n_bolos = dblarr(nmaps)
  openw, badmaps, '/data/ndhuang/badmaps.txt', /get_lun
  for i=0, nmaps - 1 do begin
     ;; catch errors
     catch, err_status
     if err_status ne 0 then begin
        print, 'Bad map: ' + !ERROR_STATE.MSG
        printf, badmaps, mapfiles[i]
        continue
     endif     
     print, mapfiles[i], double(i) / nmaps
     map = hdf5_to_struct(mapfiles[i])
     inds = where(map.contents.weight gt 0, count)
     ;; if the weight map has no zeros, wtf is wrong?
     if count lt 1 then begin
        print, 'Bad map: no zeros in the weights!'
        printf, badmaps, mapfiles[i]
        continue
     endif
     
     n_bolos[i] = map.contents.n_channels

     ;; total and median weight
     med_weight[i] = median(map.contents.weight[inds])
     tot_weight[i] = total(map.contents.weight)
     
     ;; rms, calculated only on points with weight > threshold
     ;; with arcmin smoothing
     n1 = 3400
     n2 = 3400
     smooth_map = smooth(map.contents.map, 4)
     smooth_weight = smooth(map.contents.weight, 4)
     good = where(smooth_weight gt weight_thresh)
     rms[i] = stddev(map.contents.map[good])
     ;; apparently the map structs aren't being freed correctly?
     heap_free, map
  endfor
  
  ;; save the file, then run the cuts on it
  cuts = {files: mapfiles, rms: rms, med_w: med_weight, tot_w: tot_weight}
  save, cuts, filename=directory + 'map_cuts150ghz.sav'
  close, badmaps
end
