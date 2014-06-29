pro conv_dir_to_runlist, directory, freq

;; base='/data11/cr/run3_2009b/'
;; bstub='/maps/map_'
;; estub='.fits'
;; fstubs=['150']
bstr = directory + '/' + strtrim(string(freq, '(I03)'), 2) + '/'
list = file_search(bstr + 'bundle*.fits')
ofile = bstr + 'runlist.txt'
    
len = strlen(bstr)
nl=n_elements(list)
openw,lun,ofile,/get_lun
printf, lun, '1 ' +  strtrim(string(nl), 2)
printf, lun, 'Set 1:'
for j=0,nl-1 do begin
   word=list[j]
   ;; tword=strmid(word,len,21)
   tword = word
   printf,lun,tword
endfor
free_lun,lun

end
