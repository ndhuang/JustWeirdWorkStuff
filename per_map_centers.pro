pro per_map_centers, runlist, maskfile, radec0, reso_arcmin
;; get shit from the runlist
openr,lun,runlist,/get_lun
line =''
readf,lun,line
free_lun,lun
words = strsplit(line,' ',/regex,/extract)
nset = n_elements(words)-1
if fix(words[0]) ne nset then stop
if nset lt 1 then stop

nperset =fix(words[1:*])
if min(nperset) lt 1 then stop
en=[0,nperset]
readcol,runlist,filenames,format='a',skipline=1
if n_elements(filenames) lt total(nperset)+nset then stop
startind = (total(en,/cum))[0:nset] + 1 + indgen(nset+1)
endind = startind[1:*]-2
startind = startind[0:nset-1]
nmap=total(nperset)

memstartind = (total(en,/cum))[0:nset-1]

;check that files are readable:
for i=0,nset-1 do for j=startind[i],endind[i] do $
    if not file_test(filenames[j],/read) then begin
    print,'Missing read permission for file '+filenames[j]
endif
;; done with fucking runlist bullshit
map_files = filenames

for i = startind[0], endind[0] - 1 do begin
   print, map_files[i]
   sources_and_center, map_files[i], maskfile, radec0, reso_arcmin, /py_map
endfor
end
