pro create_db_txt, savfile, outputdir
clusterdb_file = outputdir + '/ClusterCat_twoband.dat'
openw, cdb, clusterdb_file, /get_lun
rcvec = (findgen(12)+1.)*0.25
restore, savfile
for i = 0, n_elements(outtemp_2band) - 1 do begin
   cl = outtemp_2band[i]
   printf, cdb, cl.xpeak, cl.ypeak, cl.peaksig, rcvec[cl.whfilt]
endfor
close, cdb
end
