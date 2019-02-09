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
parser.add_argument('-in', dest="FILE_PATTERN", default="/path/to/hrrr_smoke/%Y%m%d%H/postprd/wrfnat_hrconus_{ff}.grib2", help="File pattern to .grib2 files, where {ff} is the forecast hours")
parser.add_argument('-out', dest="FILE_OUT", default="output/hrrr_smoke.mp4", help="Output video file")
parser.add_argument('-frames', dest="FRAME_OUT", default="output/frames/frame.%s.png", help="Frames out")
parser.add_argument('-start', dest="START_DATETIME", default="2018-11-08-18", help="Start date and time in format yyyy-mm-dd-hh")
parser.add_argument('-end', dest="END_DATETIME", default="2018-11-10-12", help="End date and time in format yyyy-mm-dd-hh")
parser.add_argument('-hours', dest="RESOLUTION_HOURS", default=6, type=int, help="Temporal resolution of data in hours")
parser.add_argument('-grad', dest="COLOR_GRADIENT", default="inferno", help="Inferno or magma")
parser.add_argument('-dur', dest="DURATION", default=60, type=int, help="Target duration in seconds")
parser.add_argument('-fps', dest="FPS", default=30, type=int, help="Target frames per second")
parser.add_argument('-message', dest="MESSAGE", default=11, type=int, help="Message number to parse")
parser.add_argument('-fhours', dest="TOTAL_FORECAST_HOURS", default=37, type=int, help="Total available forecast hours per datatime")
parser.add_argument('-dim', dest="OUTPUT_DIMENSIONS", default="1920x1080", help="Dimensions of output video")
parser.add_argument('-drange', dest="DATA_RANGE", default="0,200", help="Expected data range (to determine data color); reduce max for more dramatic colors")
parser.add_argument('-overwrite', dest="OVERWRITE", action="store_true")
parser.add_argument('-device', dest="BUTTERFLOW_DEVICE", default=-1, type=int, help="Set a specific butterflow device (run butterflow -d for device numbers)")
a = parser.parse_args()

# Parse arguments
startYear, startMonth, startDay, startHour = tuple([int(d) for d in a.START_DATETIME.strip().split("-")])
endYear, endMonth, endDay, endHour = tuple([int(d) for d in a.START_DATETIME.strip().split("-")])
colorGradient = getColorGradient(a.COLOR_GRADIENT)
outWidth, outHeight = tuple([int(d) for d in a.OUTPUT_DIMENSIONS.strip().split("x")])
dMin, dMax = tuple([float(d) for d in a.DATA_RANGE.strip().split(",")])
aspectRatio = 1.0 * outWidth / outHeight
padZeros = 5

# ensure output dirs exist
if not os.path.exists(os.path.dirname(a.FILE_OUT)):
    os.makedirs(os.path.dirname(a.FILE_OUT))
if not os.path.exists(os.path.dirname(a.FRAME_OUT)):
    os.makedirs(os.path.dirname(a.FRAME_OUT))

if a.TOTAL_FORECAST_HOURS < a.RESOLUTION_HOURS:
    print("Not enough forecast hours (%s) to fill resolution (%s)" % (a.TOTAL_FORECAST_HOURS, a.RESOLUTION_HOURS))
    sys.exit()

startDatetime = datetime.strptime(a.START_DATETIME, "%Y-%m-%d-%H")
endDatetime = datetime.strptime(a.END_DATETIME, "%Y-%m-%d-%H")

dt = startDatetime
frame = 1
while dt <= endDatetime:
    hours = a.RESOLUTION_HOURS if dt < endDatetime else a.TOTAL_FORECAST_HOURS
    for hour in range(hours):
        filename = dt.strftime(a.FILE_PATTERN).replace("{ff}", str(hour).zfill(2))
        if os.path.isfile(filename):
            frameFilename = a.FRAME_OUT % str(frame).zfill(padZeros)
            frame += 1

            if not os.path.isfile(frameFilename) or a.OVERWRITE:
                print("Reading %s" % filename)
                grbs = pygrib.open(filename)
                grb = grbs.message(a.MESSAGE)

                values = grb["values"]
                ny, nx = values.shape
                # lats, lons = grb.latlons()
                # print("lon shape: %s ... lat shape: %s" % (lons.shape, lats.shape))

                # print("Lat/lon in range: (%s, %s) (%s, %s)" % (lon0, lat1, lon1, lat0))
                pixels = dataToPixels(values, (dMin, dMax), colorGradient)
                im = Image.fromarray(pixels, mode="RGB")

                if nx != outWidth:
                    nratio = 1.0 * nx / ny
                    outHeight = int(round(outWidth / nratio))
                    im = im.resize((outWidth, outHeight), resample=Image.BICUBIC)

                im.save(frameFilename)
                print("Created frame: %s" % frameFilename)

            else:
                print("Already created frame: %s" % frameFilename)

        else:
            print("Could not find %s" % filename)

    print("--------")
    dt += timedelta(hours=a.RESOLUTION_HOURS)

extension = "." + a.FILE_OUT.split(".")[-1]
rawOutputfilename = a.FILE_OUT[:-len(extension)] + "_raw" + extension
if not os.path.isfile(rawOutputfilename) or a.OVERWRITE:
    print("Compiling frames...")
    command = ['ffmpeg','-y',
                '-framerate',str(a.FPS)+'/1',
                '-i', a.FRAME_OUT % ('%0'+str(padZeros)+'d'),
                '-c:v','libx264',
                '-r',str(a.FPS),
                '-pix_fmt','yuv420p',
                '-q:v','1',
                rawOutputfilename]
    print(" ".join(command))
    finished = subprocess.check_call(command)
    print("Done.")

else:
    print("Already created %s" % rawOutputfilename)

print("Interpolating frames...")
command = ['butterflow','-s',
            'a=0,b=end,dur=%s' % a.DURATION,
            '-o', a.FILE_OUT]
if a.BUTTERFLOW_DEVICE >= 0:
    command += ['-device', str(a.BUTTERFLOW_DEVICE)]
command.append(rawOutputfilename)
print(" ".join(command))
finished = subprocess.check_call(command)
print("Done.")
