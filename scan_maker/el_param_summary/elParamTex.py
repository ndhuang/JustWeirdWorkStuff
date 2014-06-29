import os
import glob
import shutil
import re
import numpy as np

fig_tmpl = '\\begin{figure}\n\
    \\centering\n\
    \\figtitle{Scan %(title)s Position}\n\
    \\includegraphics[height=.4\\textheight]{%(pos_file)s}\n\
\\end{figure}\n\
\\begin{figure}\n\
    \\centering\n\
    \\figtitle{Scan %(title)s Error}\n\
    \\includegraphics[height=.4\\textheight]{%(err_file)s}\n\
\\end{figure}\n'

def texOne(pos_name):
    shutil.copy2(pos_name, 
                 os.path.join(source_dir, os.path.basename(pos_name)))
    err_name = pos_name[:-7] + 'err.eps'
    shutil.copy2(err_name, 
                 os.path.join(source_dir, os.path.basename(err_name)))
    pos_name = os.path.basename(pos_name)
    err_name = os.path.basename(err_name)
    out = fig_tmpl % {'title': pos_name[:-8].replace('_', '\_'),
                      'pos_file': pos_name,
                      'err_file': err_name}
    return out
    
def scanSize(name):
    name = os.path.basename(name)
    match = re.match('.*-(\d+)p(\d)ams.*', name)
    if match is None:
        raise ValueError("%s does not look like a scan name" %name)
    size = float(match.group(1)) + float(match.group(2)) / 10
    return size

if __name__ == '__main__':
    outname = 'plots.tex'
    image_dir = '/home/ndhuang/plots/scan_profiles/stacks/'
    source_dir = '/home/ndhuang/code/scan_maker/el_param_summary'
    images = np.array(glob.glob(os.path.join(image_dir, '*pos.eps')))
    step_sizes = np.array(map(scanSize, images))
    inds = np.argsort(step_sizes)
    images = images[inds]

    outfile = open(outname, 'w')    
    for i, im in enumerate(images):
        outfile.write(texOne(im))
        if i % 4 == 0 and i > 0:
            outfile.write('\clearpage\n')
    outfile.write('\clearpage\n')
    outfile.close()
