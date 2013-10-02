function group_to_struct, file_id, groupname, objname
  forward_function group_to_struct
  ;; if n_elements(objname) eq 0 then objname = ''

  ;; deal with trailing /.  Hacky
  spl = strsplit(groupname, '/', /extract)
  groupname = '/' + strjoin(spl, '/')
  ;; print, groupname
  ;; print, objname

  ;; if the object is not a group, do stuff with it
  objinfo = h5g_get_objinfo(file_id, groupname + '/' + objname)
  type=objinfo.type
  objinfo=0
  if type ne 'GROUP' then begin
     ;; load the data, return it
     ;; print, objname, 'nongroup'
     spl = strsplit(objname, '-', /extract)
     tagname = strjoin(spl, '_')
     dat_id = h5d_open(file_id, groupname + '/' + objname)
     data = h5d_read(dat_id)
     h5d_close,dat_id
     return, data
  endif

  ;; if the object is a group, run this function on it
  n = h5g_get_nmembers(file_id, groupname + '/' + objname)
  output_struct = 0
  ;; print, file_basename(groupname)
  for i=0, n - 1 do begin
     subgroup = h5g_get_member_name(file_id, groupname + '/' + objname, i)
     tagname = file_basename(subgroup)
     ;; clean tagnames for invalid chars
     spl = strsplit(tagname, '-', /extract)
     tagname = strjoin(spl, '_')
     if i eq 0 then begin
        output_struct = create_struct(tagname, group_to_struct(file_id, groupname + '/' + objname, subgroup))
     endif else begin
        output_struct = create_struct(output_struct, tagname, group_to_struct(file_id, groupname + '/' + objname,subgroup))
     endelse
  end
  return, output_struct
end
