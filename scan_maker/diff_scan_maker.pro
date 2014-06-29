pro diff_scan_maker, scan_size, v_scan, a_max, step_size, el=el

; without /el (az scan), x is az, y is el
; with /el (el scan), x is el, y is az

; make the regular scan, then the pre scan

rate = 100D ; scan files are 100 hz

t_acc = v_scan / a_max
n_acc = int(t_acc * rate)
if n_acc mod 2 eq 1 then n_acc = n_acc + 1
t_scan = scan_size / v_scan
n_scan = int(t_scan * rate)

n_jrk = n_acc / 2 - 1
t_acc = double(n_acc) / rate
max_x_jrk =  a_max / (t_acc / 2)
x_jrk = [replicate(max_x_jrk, n_jrk), replicate(-max_x_jrk, n_jrk), replicate(0, n_acc), replicate(-max_x_jrk, n_jrk), replicate(max_x_jrk, n_jrk)]
x_jrk = [0, x_jrk, -x_jrk, 0]
x_acc = total(x_jrk, /cumulative) / rate

;; x_vel = double(replicate(1, n_scan)) * v_scan
