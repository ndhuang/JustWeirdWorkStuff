pro make_clusterlist_catalog_sptpol, coadd_dir, field, radec0, ptsrcfile
szbands = [91.2, 146.0] ; 2012 band centers

;; coadd_dir='/data39/ndhuang/clusters/ra23h30dec-55/run2/bundles2/'
coaddfile = coadd_dir + '/coadd.sav'
maskfile = coadd_dir + '/150ghz_mask.fits'
psdfiles = coadd_dir + 'field_scaling/' + ['/090ghz_', '/150ghz_'] + 'psd.sav'
;; psdfiles = coadd_dir + '/150ghz_psd.sav'

outputdir = coadd_dir + '/cluster_out/psd_test/'
file_mkdir, outputdir
savefile = outputdir+'clusters_3-sigma.sav'
savefileall = outputdir+'clusters_allinfo_3-sigma.sav'
filt_area_file = outputdir + 'filtered_area.sav'
sz_maps_file = outputdir + 'sz_maps.sav'

cmbfile='/home/ndhuang/code/clusterFinding/params/ml_l10000_acc2_lensedCls.dat'
fileksz = '/home/ndhuang/code/clusterFinding/params/ksz_sehgal.dat'
profilefile='/home/ndhuang/code/clusterFinding/profiles/profiles_12_beta1_rc025_rc300.sav'

noise1sig=[1e9,1e9,1e9] ; expect ignored (as of 2015/05/27 it is)
proj=0


clusterfind_autotools, coaddfile, radec0, maskfile, cmbfile, /cambcl,$
  profilefile,ptsrcfile,noise1sig,proj,savefile, beams = [1.7, 1.14],$
  psd_files=psdfiles,fileksz=fileksz,/saveall, savefileall=savefileall,$
  hpf=0.306, lpf = 15.278, isohpf = 400,$
  onlyuse=1,bands=[90, 150],szbands=szbands, $
  ;; bands = [150], szbands = 146.0, $
  filt_area_file = filt_area_file, szmaps_file = sz_maps_file
end
