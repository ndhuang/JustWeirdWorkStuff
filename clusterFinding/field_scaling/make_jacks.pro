pro make_jacks, data_dir, freq, runlist
sfreq = strtrim(string(freq, format = '(I03)'),2)
freq_name =  sfreq + 'ghz'
mask_file = data_dir + '/' + freq_name + '_mask.fits'
jack_file = data_dir + '/field_scaling/' + freq_name + '_100_jacks.sav'
psd_file = data_dir + 'field_scaling/' + freq_name + '_100_psd.sav'

psd = estimate_2d_psd_from_maps_multifield(runlist,apodfile=mask_file,$
                                           freq=freq, jackfile=jack_file,$
                                           njacks=100,MAPNAME='MAP')
save, psd, filename = psd_file
end
