pro make_mapcuts, savefile, outfile
  restore, savefile
  med_rms = median(cuts.rms)
  good = where(cuts.rms le 3 * med_rms and $
               cuts.rms ge .75 * med_rms and $
               cuts.med_w le 1e8, complement = bad)
  
  openw, output, outfile, /get_lun
  for i=0, n_elements(good) - 1 do begin
     printf, output, cuts.files[good[i]]
  endfor
print, float(n_elements(good)) / n_elements(cuts.files)
end
