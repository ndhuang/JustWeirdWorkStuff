import argparse
import os
import matplotlib
matplotlib.use('Agg')
from matplotlib import cm, pyplot as pl
import numpy as np
import sptpol_software.util.files as files

fig_tmpl = "\\begin{figure}[h]\n\
\\centering\n\
\\includegraphics[width=.9\\linewidth]{%s}\n\
\end{figure}\n\
"

def properPSD(psd, ell):
    inds = np.argsort(ell)
    psd = psd[inds]
    for i, row in enumerate(psd):
        psd[i] = row[inds]
    return psd

def plot2d(psd, ell, band, plotdir):
    figure = pl.figure()
    pl.imshow(np.log(psd), cmap = cm.gray)
    ax = figure.axes[0]
    tick_loc = np.arange(0, 9) * len(ell) / 8
    ax.set_xticks(tick_loc)
    ax.set_yticks(tick_loc)

    tick_val = np.arange(-4, 5) * min(ell) / 4
    ax.set_xticklabels(tick_val, rotation = 15)
    ax.set_yticklabels(tick_val)
    
    pl.xlabel('$l_x$')
    pl.ylabel('$l_y$')
    pl.title('Log(noise PSD) for %d GHz' %band)
    pl.colorbar()
    savename ='%d_2dpsd.png' %band
    pl.savefig(os.path.join(plotdir, savename))
    pl.close(figure)
    return fig_tmpl %savename

def plot1d(psd, ell, band, plotdir):
    figure = pl.figure()
    pl.subplot(211)
    pl.plot(np.fft.fftshift(ell), np.mean(psd, 0))
    pl.title('%d GHz $l_x$ PSD' %band)
    pl.xlabel('$l_x$')
    pl.ylabel('K$_\mathrm{CMB}$')

    pl.subplot(212)
    pl.plot(np.fft.fftshift(ell), np.mean(psd, 1))
    pl.title('%d GHz $l_y$ PSD' %band)
    pl.xlabel('$l_y$')
    pl.ylabel('K$_\mathrm{CMB}$')

    pl.tight_layout()
    savename ='%d_1dpsd.png' %band
    pl.savefig(os.path.join(plotdir, savename))
    pl.close(figure)
    return fig_tmpl %savename

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('psddir', type = str)
    parser.add_argument('--band', default = None, type = int)
    parser.add_argument('--plot-dir', default = '', dest = 'plotdir')
    parser.add_argument('--tex-file', default = None, type = str)
    args = parser.parse_args()
    if args.band is None:
        args.band = [90, 150]
    else:
        args.band = [args.band]
    if args.tex_file is not None:
        texfile = open(args.tex_file, 'a')
        texfile.write('\\clearpage\n')
    else:
        texfile = None
        
    for band in args.band:
        band_name = '%03dghz' %band
        psd = files.read(os.path.join(args.psddir, band_name + '_psd.fits'))
        ell = np.fft.fftfreq(np.shape(psd.psd.psd)[0], 
                             np.pi / (4 * 60 * 180)) * 2 * np.pi
        psd = properPSD(psd.psd.psd, ell)
        tex_2d = plot2d(psd, ell, band, args.plotdir)
        tex_1d = plot1d(psd, ell, band, args.plotdir)
        if texfile is not None:
            texfile.write(tex_2d + '\n')
            texfile.write(tex_1d + '\n')

    if texfile is not None:
        texfile.close()
