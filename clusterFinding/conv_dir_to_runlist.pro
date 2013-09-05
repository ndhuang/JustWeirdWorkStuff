pro conv_dir_to_runlist

;; base='/data11/cr/run3_2009b/'
;; bstub='/maps/map_'
;; estub='.fits'
;; fstubs=['150']
bstr = '/home/ndhuang/data/clusters/ra23h30dec-55/maps/run1/fits/bundles_v0/'
list = file_search(bstr + 'bundle*150ghz.fits')
ofile='/home/ndhuang/data/clusters/ra23h30dec-55/maps/run1/fits/bundles_v0/runlist_150ghz.txt'
    
len = strlen(bstr)
nl=n_elements(list)
openw,lun,ofile,/get_lun
for j=0,nl-1 do begin
   word=list[j]
   ;; tword=strmid(word,len,21)
   tword = word
   printf,lun,tword
endfor
free_lun,lun

end
