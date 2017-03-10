pro weight_coadd, output_dir, freq, runlist
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
freq_name = strtrim(string(freq, format = "(I03)"), 2) + 'ghz'
coadd_fits_file = output_dir + '/' + freq_name + '_coadd.fits'
coadd_save_file = output_dir + '/coadd.sav'
;; map_dir = input_dir + "/*" + sfreq + "ghz.h5"
mask_output_file = output_dir + '/' + freq_name + '_mask.fits'
;; map_files = file_search(map_dir)
map_files = filenames

;; mask = read_spt_fits('/data39/ndhuang/clusters/ra23h30dec-55/run1/bundles/abbys_bundles/mask_150ghz.fits')

for i = startind[0], endind[0] - 1 do begin
   print, map_files[i]
   map = read_spt_hdf5(map_files[i], /py_map)
   if i eq startind[0] then begin
      size = size(map.map.map, /dimensions)
      weight = dblarr(size[0], size[1])
      coadd = dblarr(size[0], size[1])
   endif
   coadd += map.map.map * map.weight.weight
   weight += map.weight.weight[*, *, 0, 0]
   ;; print, map_files[i]
   ;; good=where(weight ne 0, count)
   ;; if count eq 0 then print, stddev(coadd  * mask.masks.apod_mask / weight) $
   ;; else print, stddev(coadd[good] * mask.masks.apod_mask[good] / weight[good])
endfor
good=where(weight ne 0,complement=bad)
if n_elements(bad) lt 1 then coadd[bad] = 0
if n_elements(good) lt 1 then begin  
   print, 'Borked!!!!' 
   stop
endif

coadd[good] /= weight[good]

coadd_struct = {map: coadd, weight: weight, files: map_files}
create_spt_fits_file, coadd_fits_file
add_bintab_to_fits, coadd_fits_file, coadd_struct, 'coadd'

;; if the coadd save file exists, restore it and overwrite with new data
if file_test(coadd_save_file) eq 1 then restore, coadd_save_file $
else maps = dblarr(size[0], size[1], 2)

if freq eq 90 then maps[*, *, 0] = coadd $
else maps[*, *, 1] = coadd
save, maps, filename = coadd_save_file
;; save, coadd, filename = '/data/ndhuang/test/clusters/' + freq_name + '_coadd.sav'
CREATE_APODIZATION_MASKS, weight, mask_output_file, threshold=.8
end
