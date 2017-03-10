import glob
import os
from argparse import ArgumentParser

figtitle_tmpl = '\\begin{figure}\n\
    \\centering\n\
    \\figtitle{%(title)s}\n\
    \\includegraphics[height=.4\\textheight]{%(fig_file)s}\n\
\\end{figure}\n'

fig_tmpl = '\\begin{figure}[h]\n\
    \\centering\n\
    \\includegraphics[height=.3\\textheight]{%(fig_file)s}\n\
\\end{figure}\n'

preamble_tmpl = '\\documentclass{article}\n\
\\usepackage[margin=.5in]{geometry}\n\
\\usepackage[pdftex]{graphicx}\n\
\\usepackage{caption}\n\
\\usepackage{subcaption}\n\
\\graphicspath{{%(fig_dir)s}}\n\
\\newcommand{\\figtitle}[1]{\n\
  {\n\
    \\centering\n\
    \\large\\textbf{#1}\n\
    \\par\\medskip\n\
  }\n\
}\n\
\n\
\\begin{document}\n'

def texOne(fig_name, title = None):
    fig_name = os.path.basename(fig_name)
    if title is None:
        title = '.'.join(fig_name.split('.')[:-1])
    elif title == '':
        return fig_tmpl % {'fig_file': fig_name}
    out = figtitle_tmpl % {'title': title.replace('_', ' '),
                      'fig_file': fig_name}
    return out

if __name__ == '__main__':
    parser = ArgumentParser(description = 'Make a tex document of figures from a directory')
    parser.add_argument('fig_dir', type = str, help = 'Directory of plots')
    parser.add_argument('out_file', type = str, help = 'Path to file in which the tex source will be placed')
    parser.add_argument('--glob', type = str, help = 'A bash-style regex used to search within the fig_dir')
    args = parser.parse_args()
    if args.glob is None:
        figs = glob.glob(os.path.join(args.fig_dir, '*'))
    else:
        figs = glob.glob(os.path.join(args.fig_dir, args.glob))        
    figs = sorted(figs)
    outfile = open(args.out_file, 'w')
    outfile.write(preamble_tmpl % {'fig_dir': args.fig_dir})
    for i, fig in enumerate(figs):
        outfile.write(texOne(fig, title = ''))
        if (i - 1) % 2 == 0:
            outfile.write('\clearpage\n')
    outfile.write('\end{document}\n')
    outfile.close()
