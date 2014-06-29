import numpy as np

RATE = 100.0 # the frequency (Hz) of the scan file

def scanConstJerk(scan_size, v_scan, a_max):
    '''
    Create the "standard" scan.  This means acceleration happens with constant
    jerk, up to a maximum.  The telescope is instantaneously stopped at either
    end of the scan.
    '''
    raise NotImplementedError('Write me!')

def writeScanFile(az, el, scan_flags, filename):
    '''
    Write a scan file given `az` and `el`.
    The format is:
    MSPERSAMPLE <ms between samples>
    sample_number delta_az delta_el scan_flag
    where the scan_flag is 1 if we are in the constant velocity region
    '''
    f = open(filename, 'w')
    # calculate the differential pointing
    d_az = differ(az, dx = 1)
    d_el = differ(el, dx = 1)
    # tell the scan the time between samples in ms
    f.write('MSPRESAMPLE %d\n ' %(1000 / RATE))
    for i in range(len(az)):
        f.write('%d\t%0.7f\t%0.7f\t%d\n' %(i, d_az[i], d_el[i], scan_flags[i]))
    f.close()

def integrate(y, dx = 1 / RATE):
    Y = np.zeros(len(y))
    y_ext = np.concatenate(([0], y))
    for i in range(len(Y)):
        Y[i] = np.sum(y[0:i + 1]) * dx
    Y[0] = 0.
    return Y

def differ(y, dx = 1 / RATE):
    return np.diff(np.concatenate(([0], y))) / dx

def smoothAcc(scan_size, v_scan, a_max, step_size, filename = 'test.scan', elscan = False):
    '''
    This is Jason's complicated but ideal-ish scan.
    Instead of having a=v=0 at the beginning of each scan, we will have
    a = max(a), v = 0.  The step will happen over the entire turnaround.
    '''
    # let's use sane data types so we don't accidentally do int division
    scan_size = float(scan_size)
    v_scan = float(v_scan)
    a_max = float(a_max)
    step_size = float(step_size)
    # the first part of this calculation will be done in semi-arbitrary units
    # for example: arbitrary-unit-of-anlge / second for velocity
    # the scan starts with half of a triangular acc profile    
    t_acc = v_scan / a_max * 2
    n_acc = int(t_acc * RATE)
    if n_acc % 2 == 1:
        # we need an even number of samples
        # lower acc is ok, so add one to make it even
        n_acc += 1
    t_scan = scan_size / v_scan
    n_scan = int(t_scan * RATE)

    # we're going to break each turn around into two pieces, such that each 
    # one has constant jerk.  When combined, they produce a triangular profile
    # ramp up the acc
    x_jrk = np.ones(n_acc)
    x_turn1_acc = np.cumsum(x_jrk) / RATE
    x_turn1_acc /= max(abs(x_turn1_acc))

    # ramp down the acc
    x_turn2_acc = x_turn1_acc[::-1]

    # now, assemble the entire scan
    x_acc = np.concatenate((x_turn2_acc, # initial acceleration from v = 0
                            np.zeros(n_scan), # const vel region
                            -x_turn1_acc, # back to v = 0
                            -x_turn2_acc, # back to cv
                            np.zeros(n_scan), # cv
                            x_turn1_acc)) # and back to our starting point
    
    # get velocity, convert to real units, normalize
    x_vel = np.cumsum(x_acc) / RATE
    x_vel = x_vel / max(x_vel) * v_scan # d/s
    
    # get position, acc and jerk in real units
    x_pos = np.cumsum(x_vel) / RATE
    x_acc = differ(x_vel)
    x_jrk = differ(x_acc)

    # the step will also happen in two pieces.  It starts at the end of a scan
    y_jrk = np.concatenate((np.ones(n_acc / 2), -np.ones(n_acc / 2)))
    y_h1_acc = np.cumsum(y_jrk)

    # second half (at the beginning of the scan)
    y_jrk = np.concatenate((-np.ones(n_acc / 2), np.ones(n_acc / 2)))
    y_h2_acc = np.cumsum(y_jrk)

    y_acc = np.concatenate((y_h2_acc, # last half of the step
                            np.ones(2 * (n_scan + n_acc)) * step_size / 2,
                            y_h1_acc))
    # need to offset velocity correctly.  It doesn't start at 0!
    # y_vel = np.cumsum(y_acc)
    # y_pos = np.cumsum(y_vel)
    
    return y_pos, y_vel, y_acc, y_jrk
    
    
def noAzStopHalfEl(scan_size, v_scan, a_max, step_size, filename = 'test.scan', elscan = False):
    '''
    Bill's "simplest thing to do"
    Normal scan, without the az pause, and the el step spread over
    the decellaration portion of the az.
    '''
    # let's use sane data types so we don't accidentally do int division
    scan_size = float(scan_size)
    v_scan = float(v_scan)
    a_max = float(a_max)
    step_size = float(step_size)
    # the first part of this calculation will be done in semi-arbitrary units
    # for example: arbitrary-unit-of-anlge / second for velocity
    # minimizing jerk means a triangular acc profile, so we can calculate time
    t_acc = v_scan / a_max * 2 # time to accelerate from 0 to v_scan
    n_acc = int(t_acc * RATE)
    if n_acc % 2 == 1:
        # we need an even number of samples
        # lower acc is ok, so add one to make it even
        n_acc += 1
    t_scan = scan_size / v_scan
    n_scan = int(t_scan * RATE)

    # initial acceleration phase
    x_jrk = np.concatenate((np.ones(n_acc / 2), -np.ones(n_acc / 2)))
    x_init_acc = np.cumsum(x_jrk) / RATE
    x_init_acc /= max(abs(x_init_acc))
    x_acc = np.concatenate((x_init_acc, np.zeros(n_scan)))

    # turnaround
    x_jrk = np.concatenate((-np.ones(n_acc), np.ones(n_acc)))
    turn_acc = np.cumsum(x_jrk) / RATE
    turn_acc /= max(abs(turn_acc))
    x_acc = np.concatenate((x_acc, turn_acc, np.zeros(n_scan), x_init_acc))

    x_vel = np.cumsum(x_acc) / RATE
    print x_vel
    # convert to degrees / second
    x_vel = x_vel / max(abs(x_vel)) * v_scan

    # we now have our velocity profile, so let's calculate acc and position
    x_acc = differ(x_vel)
    x_jrk = differ(x_acc)
    x_pos = np.cumsum(x_vel) / RATE

    if max(abs(x_acc)) - a_max > 1e-6:
        raise RuntimeError('I got a higher max acc than you requested in the scan.  You\'re going to have to fix this')

    # now deal with the step.
    # We want the step to take part over the final deceleartion
    # again, the first part of this uses arbitrary angular units
    y_jrk = np.concatenate((np.ones(n_acc / 4), -np.ones(n_acc / 2), np.ones(n_acc / 4)))
    y_acc = np.cumsum(y_jrk) / RATE
    y_acc /= max(abs(y_acc))
    y_vel = np.cumsum(y_acc) / RATE
    y_vel /= max(abs(y_vel))
    y_pos = np.cumsum(y_vel) / RATE
    # now normalize to the correct step size in degrees
    y_pos = y_pos / max(abs(y_pos)) * step_size
    # this is just the step.  We need vel for the entire scan
    y_pos = np.concatenate((np.zeros(len(x_pos) - len(y_pos)), y_pos))
    # calculate acc and vel from the normalized position
    y_vel = differ(y_pos)
    y_acc = differ(y_vel)

    if max(abs(y_acc)) - a_max > 1e-6:
        raise RuntimeError('I got a max acceleration higher than you requested in the step.  You\'re going to have to fix this.')

    # build the scan flags
    scan_flags = np.zeros(len(x_pos))
    for i, v in enumerate(x_vel):
        if abs(abs(v) - v_scan) < 1e-13 and abs(x_acc[i]) < 1e-13:
            scan_flags[i] = 1

    # writ the scan file
    if not elscan:
        writeScanFile(x_pos, y_pos, scan_flags, filename)
    else:
        writeScanFile(y_pos, x_pos, scan_flags, filename)
    return x_pos, x_vel, x_acc, x_jrk
