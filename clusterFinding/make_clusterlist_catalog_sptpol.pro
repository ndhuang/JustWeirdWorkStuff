pro make_clusterlist_catalog_sptpol,forceaz=forceaz,forcesingle=forcesingle,stopit=stopit
field='ra23h30dec-55'
onlyuse=1

cdir='/data39/ndhuang/clusters/ra23h30dec-55/run1/bundles/abbys_bundles/'
coaddfile=cdir+'coadd.sav'
maskfile =cdir+'mask_150ghz.fits'
if keyword_set(stopit) then stop


ptsrcfile='/home/ndhuang/spt_code/sptpol_software/config_files/ptsrc_config_ra23h30dec-55_liz20121012.txt'

radec0=[352.5, -55]

cmbfile='/home/ndhuang/code/clusterFinding/params/ml_l10000_acc2_lensedCls.dat'

profilefile='/home/ndhuang/code/clusterFinding/profiles/profiles_12_beta1_rc025_rc300.sav'

noise1sig=[1e9,1e9,1e9] ; expect ignored
outputdir='/data39/ndhuang/clusters/ra23h30dec-55/cluster_out/'
savefile=outputdir+'clusters_'+field+'.sav'
savefileall=outputdir+'clusters_allinfo_'+field+'.sav'
if keyword_set(forcesingle) then begin
savefile=outputdir+'clusters_150_'+field+'.sav'
savefileall=outputdir+'clusters_150_allinfo_'+field+'.sav'
endif
proj=0
psdfiles=cdir+'psd_'+['90', '150']+'ghz.sav'
fileksz = '/home/ndhuang/code/clusterFinding/params/ksz_sehgal.dat'
if keyword_set(forceaz) then begin
    savefile=outputdir+'clusters_'+field+'-az.sav'
savefileall=outputdir+'clusters_allinfo_'+field+'-az.sav'
endif else $
  if field eq 'ra21hdec-50' then fracelscan=0.67


if field eq 'ra21hdec-50-el' then elscan=1


clusterfind_autotools,coaddfile,radec0,maskfile,cmbfile,/cambcl,$
  profilefile,ptsrcfile,noise1sig,proj,savefile,$
  psd_files=psdfiles,fileksz=fileksz,/saveall,savemem=0,hpf=0.278,$
  savefileall=savefileall,fracelscan=fracelscan,elscan=elscan,isohpf=500,$
  onlyuse=onlyuse,bands=[150, 90]
end
