from datetime import datetime
import pytz

def mkWiki(timestr):
    dt_utc = datetime.strptime(timestr, '%y%m%d %H:%M:%S')
    dt_utc = dt_utc.replace(tzinfo=pytz.utc)
    dt_local = dt_utc.astimezone(pytz.timezone('Antarctica/McMurdo'))
    header = '== %s ==' %dt_local.strftime('%Y-%m-%d')
    line = ' * %s (%s)' %(dt_local.strftime('%H:%M %Z'), 
                          dt_utc.strftime('%H:%M %Z %m-%d'))
    return header, line


if __name__ == '__main__':
    import sys
    for line in mkWiki(' '.join(sys.argv[1:])):
        print line
