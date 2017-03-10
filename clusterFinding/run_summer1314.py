import os
from field_centers import centers
# fields = ['ra23hdec-35', 'ra1hdec-35', 'ra3hdec-35', 'ra3hdec-25']
fields = ['ra5hdec-35']
for field in fields:
    field_dir = os.path.join('/mnt/rbfa/ndhuang/maps/clusters/run3_combined_ps_nolin', field)
    cmd = './mega_cluster_script.sh {field_dir!s} {field!s} {ra0:f} {dec0:f} 2>&1 |tee {field_dir!s}/`date +%Y%m%d_%H%M.log`'.format(field_dir = field_dir, field = field, ra0 = centers[field][0], dec0 = centers[field][1])
    print cmd
    os.system(cmd)

