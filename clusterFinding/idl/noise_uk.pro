pro noise_uk, coadd_dir, freq, texfile=texfile
sfreq = strtrim(string(freq, format = '(I03)'),2)
freq_name =  sfreq + 'ghz'
mask_file = coadd_dir + '/' +  freq_name + '_mask.fits'
runlist = coadd_dir + '/' + freq_name + '_runlist.txt'

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

weight_map = dblarr(3360, 3360)
coadd_map = dblarr(3360, 3360)

if endind[0] - startind[0] mod 2 eq 1 then begin
   endind[0] = endind[0] - 1
endif
rand = randomu(seed, endind[0] - startind[0])
rand_inds = sort(rand) + 1
for i = 0, endind[0] - startind[0] - 1 do begin
   map = read_spt_hdf5(filenames[rand_inds[i]], /c_map)
   if i mod 2 eq 1 then begin
      coadd_map += map.map.map * map.weight.weight
   endif else begin
      coadd_map -= map.map.map * map.weight.weight
   endelse
   weight_map += map.weight.weight
endfor
mask = read_spt_fits(mask_file)
good = where(weight_map gt 0, count, complement = bad)
if count ne 0 then coadd_map[good] = (coadd_map[good]  / weight_map[good])
coadd_map[bad] = 0
coadd_map *= mask.masks.apod_mask
good = where(mask.masks.apod_mask gt 0.999)
noise_uk = stddev(coadd_map[good]) * .25 * 1e6
if n_elements(texfile) eq 0 then begin
   print, 'uK-arcmin: ', noise_k
endif else begin
   openw, lun, texfile, /get_lun, /append
   printf, lun, sfreq + " & " + strtrim(string(noise_uk, format = '(F0.3)')) + "\\"
   free_lun, lun
endelse
end
