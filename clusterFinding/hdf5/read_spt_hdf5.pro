function read_spt_hdf5, filename, c_map=c_map, py_map=py_map
  struct = hdf5_to_struct(filename)
  if keyword_set(c_map) then begin
     ;; make it look like a map structure that spt_analaysis expects
     old = struct
     if size(old.map.weight_map, /n_dimensions) gt 2 then begin
        ;; polarization map
        struct = {map: {map: old.map.real_map_T}, weight: {weight: reform(old.map.weight_map[0, 0, *, *])}}
     endif else begin
        ;; t-only
        struct = {map: {map: old.map.real_map_T}, weight: {weight: reform(old.map.weight_map)}}
     endelse
  endif
  if keyword_set(py_map) then begin
     ;; make it look right.  doesn't work for polarization maps
     old = struct.contents
     if old.weighted_map then begin 
        map = old.map / old.weight
     endif else map = old.map
     struct = {map: {map: old.map}, weight: {weight: old.weight}}
  endif
  return, struct
end
