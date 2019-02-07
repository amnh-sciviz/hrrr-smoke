# -*- coding: utf-8 -*-

import argparse
from lib import *
import numpy as np
import os
from PIL import Image
from pprint import pprint
import pygrib
import sys

# Input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="/path/to/hrrr_smoke/2018110818/postprd/wrfnat_hrconus_00.grib2", help=".grib2 file to inspect")
parser.add_argument('-inventory', dest="SHOW_INVENTORY", action="store_true")
parser.add_argument('-keys', dest="SHOW_KEYS", action="store_true")
parser.add_argument('-kv', dest="KEY_VALUES", default="", help="Display all the values of key")
parser.add_argument('-message', dest="MESSAGE", default=0, type=int, help="Show message")
a = parser.parse_args()

print("Reading GRIB file...")
grbs = pygrib.open(a.INPUT_FILE)

if a.SHOW_INVENTORY:
    print("\nInventory:")
    for grb in grbs:
        print(grb)

if len(a.KEY_VALUES) > 0:
    print("\nAll values for key %s" % a.KEY_VALUES)
    values = []
    for grb in grbs:
        value = grb[a.KEY_VALUES]
        values.append(value)
    for v in sorted(list(set(values))):
        print(v)

if a.SHOW_KEYS:
    if a.MESSAGE > 0:
        grb = grbs.message(a.MESSAGE)
    else:
        grb = grbs.read(1)[0]
    print("\nKeys:")
    for i, key in enumerate(grb.keys()):
        try:
            print("%s. %s=%s" % (i+1, key, grb[key]))
        except RuntimeError:
            pass
