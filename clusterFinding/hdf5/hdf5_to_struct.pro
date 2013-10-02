function hdf5_to_struct, filename
  file_id = h5f_open(filename)
  n = h5g_get_nmembers(file_id, '/')
  for i = 0, n - 1 do begin
     groupname = h5g_get_member_name(file_id, '/', i)
     if i eq 0 then begin
        output = create_struct(groupname, group_to_struct(file_id, '/', groupname))
     endif else begin
        output = create_struct(output, create_struct(groupname, group_to_struct(file_id, '/', groupname)))
     endelse
  endfor
  h5f_close, file_id
  return, output
end
