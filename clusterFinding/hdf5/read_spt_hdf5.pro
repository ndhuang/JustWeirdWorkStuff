function read_spt_hdf5, filename, c_map=c_map
  struct = hdf5_to_struct(filename)
  if keyword_set(c_map) then begin
     ;; make it look like a map structure that spt_analaysis expects
     old = struct
     struct = {map: {map: old.map.real_map_T}, weight: {weight: old.map.weight_map[*,*, 0, 0]}}
     ;; struct.map.map = struct.map.real_map_T
     ;; struct.map.weight = struct.map.weight_map
  endif
  return, struct
end
