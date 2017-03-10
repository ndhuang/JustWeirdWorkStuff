"""
Make random bundles
"""

import argparse
import numpy as np
from sptpol_software.util import files

def makeBundle(mapfiles):
    bundle = files.read(mapfiles[0])
    for mf in mapfiles[1:]:
        bundles += files.read(mf)
