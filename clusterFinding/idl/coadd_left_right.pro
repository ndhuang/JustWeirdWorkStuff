pro coadd_left_right, band
  dir = '/data39/ndhuang/clusters/ra23h30dec-55/run3/map/ra23h30dec-55/'
  openr, lgoodmaps, dir + 'left/good_' + strtrim(string(band, format = '(I03)')) + '_maps.txt', /get_lun
  openr, rgoodmaps, dir + 'right/goodmaps_' + strtrim(string(band, format = '(I03)')) + 'ghz.txt', /get_lun
  larray = ''
  rarray = ''
  line = ''
  while not eof(lgoodmaps) do begin
     readf, lgoodmaps, line
     larray = [larray, line]
  endwhile
  free_lun, lgoodmaps
  while not eof(rgoodmaps) do begin
     readf, rgoodmaps, line
     rarray = [rarray, line]
  endwhile
  free_lun, rgoodmaps
  
  if n_elements(larray) gt n_elements(rarray) do begin
     for i = 0, n_elements(larray) do begin
        basename = file_basename(larray[i])
