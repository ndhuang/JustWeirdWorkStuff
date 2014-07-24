pro cluster_list_summary, savfile, tex, text, radec0, npix, field
openw, tex, tex, /get_lun
openw, text, text, /get_lun
restore, savfile

N = n_elements(outtemp_2band)
pix2ang_proj0, npix, radec0, .25, ra, dec, xpix=outtemp_2band.xpeak, ypix=outtemp_2band.ypeak
radii = (findgen(12) + 1) * .25

false_4 = 153
false_45 = 21
false_5 = 3
inds = where(outtemp_2band[*].peaksig gt 4.5, n45)
inds = where(outtemp_2band[*].peaksig gt 5.0, n5)
purity45 = float(false_45) / n45
purity5 = float(false_5) / n5
printf, tex, "\section{The Clusters}"
printf, tex, field + " contains " + strtrim(string(n45, format = "(I3)"), 2) + " clusters above 4.5 sigma, " + strtrim(string(n5, format = "(I3)"), 2) + " of which are above 5 sigma.  We expect approximately " + string(false_45, format = "(I3)") + " (" + strtrim(string(false_5, "(I3)"), 2) + ") false detections above 4 (5) sigma."
printf, tex, ""
printf, text, "sig        ra         dec        radius"

for i = 0, N - 1 do begin
   ra_s = string(ra[i], format = '(F7.3)')
   dec_s = string(dec[i], format = '(F7.3)')
   sig_s = string(outtemp_2band[i].peaksig, format = '(F7.3)')
   rad_s = string(radii[outtemp_2band[i].whfilt], format = '(F7.3)')

   if outtemp_2band[i].peaksig gt 4.5 then begin
      if i mod 40 eq 0 then begin
         if i gt 0 then begin
            printf, tex, "\hline"
            printf, tex, "\end{tabular}"
            printf, tex, "\clearpage"
         end
         printf, tex, "\begin{tabular}{|c|c|c|c|}"
         printf, tex, "\hline"
         printf, tex, "Significance (sigma) & RA (degrees) & dec (degrees) & radius (arcmin)\\"
         printf, tex, "\hline"
      endif
      printf, tex, sig_s + " & " + ra_s + " & " + dec_s + " & " + rad_s + "\\"
   endif
   printf, text, sig_s + "    " + ra_s + "    " + dec_s + "     " + rad_s
endfor
printf, tex, "\hline"
printf, tex, "\end{tabular}"
close, tex
close, text
end
