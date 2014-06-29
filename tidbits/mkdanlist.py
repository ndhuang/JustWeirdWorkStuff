from sptpol_software.observation.receiver import Receiver

rec = Receiver()

def isDan(channel):
    try:
        dan_gain = rec.hw_map.getBiasPropsSafe(channel, 'dan_gain')
        print dan_gain
        return dan_gain != 0
    except:
        return False


map(isDan, rec.hw_map.channels)
# print filter(isDan, rec.hw_map.channels)
