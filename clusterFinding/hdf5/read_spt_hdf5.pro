function read_spt_hdf5, filename, c_map=c_map
  struct = hdf5_to_struct(filename)
  if keyword_set(c_map) then begin
     ;; make it look like a map structure that spt_analaysis expects
     old = struct
     if size(old.map.weight_map, /n_dimensions) gt 2 then begin
        struct = {map: {map: old.map.real_map_T}, weight: {weight: reform(old.map.weight_map[0, 0, *, *])}}
     endif else begin
        struct = {map: {map: old.map.real_map_T}, weight: {weight: reform(old.map.weight_map)}}
     endelse
  endif
  return, struct
end
