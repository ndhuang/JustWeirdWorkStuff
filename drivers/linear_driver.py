import argparse

def getFreq(freq):
    return int(round(float(freq) * 50.))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("freq", type = float)
    args = parser.parse_args()
    print("MC A70 V{:d} G ".format(getFreq(args.freq)))
