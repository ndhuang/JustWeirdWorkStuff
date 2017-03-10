import sys
import time

f = open(sys.argv[1], 'a')

while True:
    msg = raw_input('> ')
    f.write('{}\t{}\n'.format(time.time(), msg))
f.close()
