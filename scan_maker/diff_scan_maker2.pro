pro diff_scan_maker2, scan_size, v_scan, a_max, step_size, fileout=fileout, stopit=stopit, el=el

;---------------------------------------------------------------------------
;  NAME:
;        diff_scan_maker.PRO
;
;  PURPOSE:
; 
;      This program creates a .scan file to move the telescope in an "s-curve" pattern in 
;	either AZ or EL. The program writes a file whose outputs are the AZ and EL differential
;	offsets (ie velocities/rate) and flags when the telescope is in scan mode and plots the scan 
;	to screen.
;
;	Typically we don't like to run the SPT with an acceleration greater than ~ 1.0 d/s/s
;
;	Make sure to convert your scan throw into dRA = dAZ/cos(EL)
;
;	Maintain the .scan file naming convention so that one can easily see what the scan does.
; 
; 	DO NOT commit ANY scan file that is misnamed.
;
;  CALLING SEQUENCE:
;
;     diff_scan_maker, 10., 0.5, 1., 0.1, fileout='del-10d-0p5ds-4dss-1ams.scan', /stopit, /el
;
;  INPUT:
;
;      scan_size = the turnaround point for the end of the scan
;               NOTE that this program will scan for this distance,
;               and does not account for the turnaround
;               WATCH the text output when you run this program for
;               the max AZ
;
;      v_scan = the desired (constant) scan velocity. 
;
;      a_max = the maximum tolerable acceleration for the scan
;              NEVER exceed 4 deg / s /s
;              NOTE that there is a slight bug or "feature" of this
;              routine that sometimes the a_max you select is not the
;              one you get.
;              WATCH the text output to tune a_max
;              after a fix, the problem seems to only be for a_max > 2 d/s/s
;
;      step_size = The desired EL step (or AZ if /el is set) in degrees. 
;
;
;      fileout = the output file name.
;		FOLLOW THE NAMING CONVENTION!
;
;  OPTIONAL INPUTS:
;	/el = this makes the .scan file scan in EL instead of AZ
;
;  OUTPUT:
;        An ASCII file with the following format:
;
;        MSPERSAMPLES 10[long]
;        INDEX[long]    AZ[double]    EL[double]   FLAG[int]
;            ...            ...            ...         ...
;
;  ROUTINES USED:
;		
;
;  AUTHOR:  JV vieira@uchicago.edu
;  DATE CREATED:  Feb. 9 2007
;  REVISION HISTORY:
;          based off of Clem's scurve_new.m program
;      
;          JV (sort of) fixed a_max problem. It breaks down only when
;          a_max > 2 d/s/s and v_scan is < 1 d/s
;          
;          JV removed rate options in input for other than 100Hz
;             added some text to plots and error messages
;
;	   JV removed some colors in the plotting and committed version 5 - 19 Feb 2008
;       
;  TO DO:
;    
;	- filter out 2.5 Hz
;   
;-------------------------------------------------

; we always print the output at 100Hz nowadays
rate=100.

if not(keyword_set(fileout)) then fileout = 'test.scan'


; for 100Hz this converts from s to 10 ms intrinsic to program for
; calculating a, v, etc
timestep=100D

;-------------
; first, calculate main scan (ussually AZ)
;-------------

; calculate how long the scan lasts, knowing, AZ and v
t_scan=double(scan_size/v_scan*timestep)

; this is for calculating how long to ramp up a
;t=timestep/a_max
t=timestep/a_max*v_scan

; this is the "jerk" or third time derivative
j = double([0, replicate(1,t), replicate(-1,t)])

; now calculate a from j
a = total(j, /cumulative) ;/timestep we don't need 

; now calculate v in the acceleration phase
v1 = total(a, /cumulative) ;/timestep we don't need timestep because it is normalized below
; normalize v1 to v_scan
v1= v1*v_scan/(v1[n_elements(v1)-1])

; constant v section
v2 = v1[n_elements(v1)-1]*replicate(1,t_scan-4)

; This is the v in the decceleration phase
v3 = reverse(v1)
; now put it all together
v = [v1, v2, v3]

; double up to make complete scan
v = [v,-v[1:n_elements(v)-1]]/timestep ; here we add timestep because to calculate x we sum

; now that we have the complete v profile, we can calculate time for
; the entire scan
time = findgen(n_elements(v))/timestep

; here we calculate position (AZ)
x = total(v, /cumulative)

; now convert to instantaneous v [deg/s]
v=v*timestep

; now re-calculate a from v
a = v - ([0,v])[0:n_elements(v)-1]
a=a*timestep ; convert to instantaneous a [deg/s/s]

; now re-calculate j from a
j = (a - ([0,a])[0:n_elements(a)-1])*timestep ; convert to [deg/s/s/s]


x_az  = x
v_az = v
a_az = a
j_az = j
size_az=n_elements(x_az)

;----------
; second, calculate secondary step (usuually EL)
;----------

; this is for calculating how long to ramp up
t=timestep*sqrt(step_size/a_max)
; note that I should add a factor of sqrt(2) here, but I don't because the 
; acceleration will sometimes be slightly higher than what I request.

; this is the "jerk" or third time derivative
j = double([0, replicate(1,t), replicate(-1,t)])

; now calculate a from j
a = total(j, /cumulative) ;/timestep we don't need 

; now calculate v in the acceleration phase
v1 = total(a, /cumulative) ;/timestep we don't need timestep because it is normalized below

; This is the v in the decceleration phase
v3 = reverse(v1)
; now put it all together
v = [v1, v3]

; now that we have the complete v profile, we can calculate time for
; the entire scan
time = findgen(n_elements(v))/timestep

; here we calculate position (AZ)
x = total(v, /cumulative)
; normalize x
x = x/max(x)*step_size

; now convert to instantaneous v [deg/s]
;v=v*timestep
v = x - ([0,x])[0:n_elements(x)-1]
v=v*timestep ; convert to instantaneous a [deg/s/s]



; now re-calculate a from v
a = v - ([0,v])[0:n_elements(v)-1]
a=a*timestep ; convert to instantaneous a [deg/s/s]

; now re-calculate j from a
j = (a - ([0,a])[0:n_elements(a)-1])*timestep ; convert to [deg/s/s/s]


x_el  = x
v_el = v
a_el = a
j_el = j
size_el=n_elements(x_el)


;------------
; now finish up
;------------



;size_tot = size_az + size_el

;x_az = [x_az, dblarr(size_el)]
;x_el = [dblarr(size_az), x_el]

;v_az = [v_az, dblarr(size_el)]
;v_el = [dblarr(size_az), v_el]

;a_az = [a_az, dblarr(size_el)]
;a_el = [dblarr(size_az), a_el]

;j_az = [j_az, dblarr(size_el)]
;j_el = [dblarr(size_az), j_el]

;time = findgen(size_tot)/100.




size_tot = size_az

x_el = [dblarr(size_az), x_el]
x_el = x_el[size_el:size_az+size_el-1]

v_el = [dblarr(size_az), v_el]
v_el = v_el[size_el:size_az+size_el-1]

a_el = [dblarr(size_az), a_el]
a_el = a_el[size_el:size_az+size_el-1]

j_el = [dblarr(size_az), j_el]
j_el = j_el[size_el:size_az+size_el-1]

time = findgen(size_tot)/100.



; now make final arrays
; they go like this:
;       x[*,0] = AZ
;       x[*,1] = EL


if not(keyword_set(el)) then begin
	x = [[x_az], [x_el]]
	v = [[v_az], [v_el]]
	a = [[a_az], [a_el]]
	j = [[j_az], [j_el]]
ENDIF ELSE BEGIN
	x = [[x_el], [x_az]]
	v = [[v_el], [v_az]]
	a = [[a_el], [a_az]]
	j = [[j_el], [j_az]]
ENDELSE




;;;;;;;;;;;;;;;;;;;;;;;;;;



; these ar for double checking that we never go over the telescope max
; a and v

max_a=max(abs(a))
min_a=min(a)

max_v=max(abs(v))
min_v=min(v)
max_x=max(x)

min_plot_az = min([x[*,0],v[*,0],a[*,0]])
min_plot_el = min([x[*,1],v[*,1],a[*,1]])

max_plot_az = max([x[*,0],v[*,0],a[*,0]])
max_plot_el = max([x[*,1],v[*,1],a[*,1]])


print, '----------------------------------------------------'
print, '   AZ                       |        EL'
print, 'max x =', max(x[*,0]),         '     |    max x =', max(x[*,1])
print, 'max v  =', max(abs(v[*,0])), '    |    max v  =', max(abs(v[*,1]))
print, 'max a  =', max(abs(a[*,0])), '    |    max a  =', max(abs(a[*,1]))
print, '----------------------------------------------------'


!p.multi = [0,1,2]

title = 'AZ     '+fileout
xtitle='time [ s ]'
ytitle='deg'

plot, time, x[*,0], yr=[min_plot_az, max_plot_az], xr=[min(time)-1, max(time)+1], title=title, xtitle=xtitle, ytitle=ytitle, /xs
oplot, time, v[*,0], linestyle=1
oplot, time, a[*,0], linestyle=2

title='EL     '+fileout
plot, time, x[*,1], yr=[min_plot_el, max_plot_el], xr=[min(time)-1, max(time)+1], title=title, xtitle=xtitle, ytitle=ytitle, /xs
oplot, time, v[*,1], linestyle=1
oplot, time, a[*,1], linestyle=2

!p.multi = 0


;--------------------
;   WRITE FILE 
;--------------------

; open output file
get_lun, scurve_file
openw, scurve_file, fileout

; initialize array for scan flag
scan_flag=intarr(size_tot)

; print the size of each time step
printf, scurve_file, 'MSPERSAMPLE ', long(1000./rate)

; initialize time index for calculating the duty cycle 
t_duty=0L

; now start loop for writing scan offsets to file 
FOR i=0L, size_tot-1 DO BEGIN

    ; this says "when |v| = v_scan  & a = 0"
    IF ( abs(abs(v_az[i])-v_scan) lt 1e-13 ) AND ( a_az[i] EQ 0 ) THEN BEGIN

            ; scan flag
            scan_flag[i]=1
            ; this is for keeping track of duty cycle
            t_duty=t_duty+1

    ENDIF

    ; this prints to file at our given rate
    IF (i mod (100./rate) eq 0) THEN BEGIN
;        if not(keyword_set(el)) then begin
            printf, scurve_file, i/(long(100./rate)), v[i,0]/100., v[i,1]/100.,  scan_flag[i]
 ;       endif else begin
  ;          printf, scurve_file, i/(long(100./rate)),v[i,1]/100., v[i,0]/100., scan_flag[i]
   ;     endelse
    ENDIF
    
   ; this prints to screen every 100th
    ; time step, just for something to
    ; look at
;    IF (i mod 100 eq 0) THEN  BEGIN
;
 ;      print, i, '     t =', time[i], '     AZ =', x[i], $
;      '     v =', v[i], '     a =', a[i], '     jerk =', j[i],  '     flag =', scan_flag[i]

;    ENDIF

ENDFOR


print, 'duty cycle =', t_duty/timestep, ' s   /', size_tot/timestep, ' s    =', float(t_duty)/float(size_tot)*100., ' %'
print, 'max a  =', max_a
print, 'max v  =', max_v
print, 'scan v =', v2[0]
print, 'max az =', max_x
print, 'AZ offset =', max_x/2.
print, 'EL step took ', size_el/100. , '  seconds.'
print, 'Output File = ', fileout
print, '----------------------------------------------------'

if not(keyword_set(el)) then begin
    print, 'This is an AZIMUTH scan'
endif else begin
    print, 'This is an ELEVATION scan'
endelse

print, '----------------------------------------------------'


IF abs( (max_a - a_max)/a_max ) GT 0.05 THEN BEGIN

    print, ' '
    print, '* * * * *'
    print, 'HEY YOU!' 
    print, 'Your maximum acceleraion is not what you intended!'
    print, 'Fix it!'
    print, 'DO NOT MAKE A .scan FILE WITH THE WRONG ACCELERATION IN THE FILE NAME!'
    print, '* * * * *'
    print, ' '

ENDIF


IF abs( max_a ) GT 4.001 THEN BEGIN

    print, ' '
    print, '* * * * *'
    print, 'HEY YOU!' 
    print, 'Your maximum acceleraion is to high!'
    print, 'Fix it!'
    print, 'The telescope cannot accelerate above 4 deg/s/s!'
    print, '* * * * *'
    print, ' '

ENDIF

; close output file
close, scurve_file
free_lun, scurve_file



;;;;;;;;;;;;;;;;;;;;;;;;;;;;



IF keyword_set(stopit) THEN stop

END
