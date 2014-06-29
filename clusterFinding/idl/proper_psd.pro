function proper_psd, psd, reso_arcmin
  ;; make your goddamn psd square
  s = size(psd)
  n = s[1]
  nyquist = 1.0 / (reso_arcmin / 60 / 180) ;; nyquist ell
  d_ell = (nyquist / n) * 2
  ell = dblarr(n)
  ellp = findgen(n / 2) * d_ell
  ellm = -(findgen(n/ 2) + 1) * d_ell
  ell[0:(n / 2) - 1] = ellp
  ell[n / 2: n - 1] = reverse(ellm)
  inds = sort(ell)
  ind1 = dblarr(n, n)
  ind2 = dblarr(n, n)
  for i=0, n - 1 do begin
     ind1[*, i] = inds
     ind2[i, *] = inds
  endfor
  return, psd[ind1, ind2]
end
  
  
