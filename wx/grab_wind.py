import time
import numpy as np
# SPT weather data   0. format version   1. server utc (mjd)   2. wx year   3. wx day in year   4. wx hour   5. wx minute   6. Internal Temperature (C)   7. Air Temperature (C)   8. Wind Direction (AZ, degrees)   9. Wind Speed (m/s)   10. Pressure (mB)   11. Relative Humidity (0-100)

wx_file = '/home/wxdata/public_html/spt_wxdata.csv'
wind_file = '/home/ndhuang/code/wx/wind.csv'
if __name__ == '__main__':
    time.sleep(30)
    data = np.loadtxt(wx_file, delimiter = ',')
    mjd_utc = data[1]
    wind_speed = data[9]
    wind_dir = data[8]
    
    wf = open(wind_file, 'a')
    wf.write("%f, %f, %f\n" %(mjd_utc, wind_speed, wind_dir))
