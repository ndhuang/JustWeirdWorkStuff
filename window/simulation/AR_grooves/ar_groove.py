import numpy as np

def fill_pyramid(z, L, solid):
    def _fill_pyramid(z, L, solid):
        if np.abs(z) <= solid:
            return 0
        else:
            return 1 - ((np.abs(z) - L) / L)**2
    if np.isscalar(z):
        return _fill_pyramid(z, L, solid)
    return np.array([_fill_pyramid(z_, L, solid) for z_ in z])

def n_eff(fill):
    n_plastic = 1.52
    return np.sqrt((1 - fill) * n_plastic**2 + fill)

def pyramids(n, ang, pitch, freq):
    j = np.complex(0, 1)
    fill = fill_pyramid
    ang = np.deg2rad(ang)
    L = pitch / (2. * np.tan(ang / 2.))
    k0 = freq * 2 * np.pi / 3e8
    # ensure an integer number of wavelengths
    wavelength = 2 * np.pi / k0
    z_slice = np.linspace(-L, L, n)
    nz = n_eff(fill(z_slice, L, 0))
    wavedist = k0 * np.trapz(nz, z_slice)
    extra_dist = wavedist % wavelength
    z_slice = np.linspace(-(L + extra_dist / 2), (L + extra_dist / 2))
    n = len(z_slice)
    dz = np.mean(np.diff(z_slice))
    Ms = np.identity(2)
    alltheMs = np.zeros([n, 2, 2], dtype = np.complex)
    for i, z in enumerate(z_slice):
        if fill(z, L, extra_dist) == 0:
            continue
        last_trig = 0
        nz = n_eff(fill(z, L, extra_dist))
        trig_arg = nz * k0 * dz
        # trig_arg = np.pi
        print trig_arg / np.pi
        M = np.array([[np.cos(trig_arg), 
                       j / nz * np.sin(trig_arg)],
                      [-j * nz * np.sin(trig_arg),
                       np.cos(trig_arg)]])
        alltheMs[i] = M
        # print M
        # print (last_trig - trig_arg) / np.pi
        Ms  = M.dot(Ms)
        # last_trig = trig_arg
        # print M
        print np.imag(2 * np.linalg.det(Ms) / np.sum(Ms))
        # print Ms[0, 0]
        # if Ms[0, 0] > 1:
        #     print i
            # break
    # print L / 25.4e-3, L
    print 2 * np.linalg.det(Ms) / np.sum(Ms)
    return alltheMs, Ms

def pyramids_analytic(n, ang, pitch, freq):
    raise NotImplementedError("It don't work")
    fill = fill_pyramid
    ang = np.deg2rad(ang)
    L = (pitch / 2.) / np.tan(ang / 2.)
    dz = 2 * L / n
    k0 = freq * 2 * np.pi / 3e8
    n_plastic = 1.52
    z_slice = np.linspace(-L, L, n)
    phase = fill_pyramid(z_slice, L) * n_plastic * k0 * dz
    diff_phase = phase[0] - sum(phase[1:])
    print diff_phase, sum(phase)
    return (np.cos(diff_phase)**2 - np.sin(sum(phase))**2) / np.cos(diff_phase)
        
if __name__ == '__main__':
    pass
