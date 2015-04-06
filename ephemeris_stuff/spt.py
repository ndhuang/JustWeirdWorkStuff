import ephem

def getSPT():
    spt = ephem.Observer()
    spt.lon = '-44.650'
    spt.lat = '-89.9911'
    spt.elevation = 2843
    spt.pressure = 800
    return spt
