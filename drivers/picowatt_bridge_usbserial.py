import Gpib, time, numpy
import serial, sys

sensors = {
#	'UCSTAGE': (0, 'RuO2_reduced.txt'),
#	'ICSTAGE': (1, 'X50962_UCSTAGE.txt'),
#	'LCBoard': (2, 'RuO2_reduced.txt'),
#	'ICHEAD': (3, 'ICheadcal.txt'),
#	'UCHEAD': (4, 'UCheadcal.txt'),
        'UCHEAD': (0, 'UCheadcal.txt'),
        'UCHEAD_GRT': (1, 'GRT_25312.txt'),
        'RuO2_1': (2, 'RuO2_reduced.txt'),
        'RuO2_2': (3, 'RuO2_reduced.txt'),
        'RuO2_3': (4, 'RuO2_reduced.txt'),
}

def send(dev, msg, term = '\n', debug = True):
        debug = debug
        if not msg.endswith(term):
                msg = msg + term
        if debug:
                print msg,
        dev.write(msg)

# meter = Gpib.Gpib('picowatt')
meter = serial.Serial('/dev/ttyUSB2', timeout = 1)
send(meter, '++addr 20\n')

send(meter, '*IDN?')
print meter.readline()
sys.exit()

header = ['Time']
for sensor in sensors:
        header += [sensor + '-R', sensor]
print '\t'.join(header)

calibrations = {}
for sensor in sensors:
	cal = numpy.loadtxt('/home/tijmen/crython/berkeley/calibrations/' + sensors[sensor][1], skiprows=1)
	if cal[0,1] > cal[1,1]:
		cal = cal[::-1]
	calibrations[sensor] = cal

send(meter, 'REM 1')
send(meter, 'INP 1')
send(meter, 'EXC 4')
send(meter, 'ARN 1')
while True:
	outline = [str(time.time())]
	for sensor in sensors:
		send(meter, 'MUX %d' % sensors[sensor][0])
		time.sleep(5)
		send(meter, 'ADC; *OPC')
		time.sleep(5)
		send(meter, '*OPC ?')
		while meter.read() != '1\n':
			time.sleep(1)
			send(meter, '*OPC ?')
		send(meter, 'RES ?')
		r = meter.read().strip().split()[1]
		t = numpy.interp(float(r), calibrations[sensor][:,1], calibrations[sensor][:,0])
		outline += [r, str(t)]
	print '\t'.join(outline)
	time.sleep(10)
