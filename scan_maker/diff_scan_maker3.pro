pro diff_scan_maker3, scan_size, v_scan, a_max, step_size, el=el

; without /el (az scan), x is az, y is el
; with /el (el scan), x is el, y is az

; make the regular scan, then the pre scan

; use sensible types
scan_size = float(scan_size)
v_scan = float(v_scan)
a_max = float(a_max)
step_size = float(step_size)

rate = 100D ; scan files are 100 hz

t_acc = v_scan / a_max
n_acc = long(t_acc * rate)
if n_acc mod 2 eq 1 then n_acc = n_acc + 1
t_scan = scan_size / v_scan
n_scan = long(t_scan * rate)

print, t_acc
print, t_scan

n_jrk = n_acc / 2 - 1
t_acc = double(n_acc) / rate
max_x_jrk =  a_max / (t_acc / 2)
x_jrk = [replicate(max_x_jrk, n_jrk), replicate(-max_x_jrk, n_jrk), replicate(0, n_acc), replicate(-max_x_jrk, n_jrk), replicate(max_x_jrk, n_jrk)]
x_jrk = [0, x_jrk, -x_jrk, 0]
x_acc = total(x_jrk, /cumulative) / rate
t = findgen(n_elements(x_jrk)) / 100
;plot, t, x_acc
end
;; x_vel = double(replicate(1, n_scan)) * v_scan
