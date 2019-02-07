# -*- coding: utf-8 -*-

import argparse
from datetime import datetime
from datetime import timedelta
from lib import *
import numpy as np
import os
from PIL import Image
from pprint import pprint
import pygrib
import subprocess
import sys

# Input
parser = argparse.ArgumentParser()
parser.add_argument('-pat', dest="FILE_PATTERN", default="/path/to/hrrr_smoke/{yyyy}{mm}{dd}{hh}/postprd/wrfnat_hrconus_{ff}.grib2", help="File pattern to .grib2 files")
parser.add_argument('-start', dest="START_DATETIME", default="2018-11-08-18", help="Start date and time in format yyyy-mm-dd-hh")
parser.add_argument('-end', dest="END_DATETIME", default="2018-11-10-12", help="End date and time in format yyyy-mm-dd-hh")
parser.add_argument('-hours', dest="RESOLUTION_HOURS", default=6, type=int, help="Temporal resolution of data in hours")
parser.add_argument('-grad', dest="COLOR_GRADIENT", default="inferno", help="Inferno or magma")
parser.add_argument('-dim', dest="OUTPUT_DIMENSIONS", default="1920X1080", help="Dimensions of output video")
parser.add_argument('-dur', dest="DURATION", default=60, type=int, help="Target duration in seconds")
parser.add_argument('-fps', dest="FPS", default=30, type=int, help="Target frames per second")
parser.add_argument('-message', dest="MESSAGE", default=11, type=int, help="Message number to parse")
parser.add_argument('-dim', dest="OUTPUT_DIMENSIONS", default="1920X1080", help="Dimensions of output video")
parser.add_argument('-bounds', dest="BOUNDS", default="-135,50,-75,50", help="Geographic boundary top left point and top right point in format: lon_tl,lat_tl,lon_tr,lat_tr")
a = parser.parse_args()

# Parse arguments
startYear, startMonth, startDay, startHour = tuple([int(d) for d in a.START_DATETIME.strip().split("-")])
endYear, endMonth, endDay, endHour = tuple([int(d) for d in a.START_DATETIME.strip().split("-")])
colorGradient = getColorGradient(a.COLOR_GRADIENT)
outWidth, outHeight = tuple([int(d) for d in a.OUTPUT_DIMENSIONS.strip().split("x")])
lonTL, latTL, lonTR, latTR = tuple([float(d) for d in a.BOUNDS.strip().split(",")])
