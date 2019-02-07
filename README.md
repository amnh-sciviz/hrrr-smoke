# HRRR Smoke Visualization

Repository for visualizing [HRRR smoke data from NOAA](https://rapidrefresh.noaa.gov/hrrr/HRRRsmoke/)

## Requirements

- [Python](https://www.python.org/) 2.7+ or 3+
- [PyGRIB](https://github.com/jswhit/pygrib) for reading .grib2 files, which has a number of dependencies:
  - [NumPy](http://www.numpy.org/)
  - [PyProj](https://github.com/jswhit/pyproj)
  - [ecCodes](https://confluence.ecmwf.int//display/ECC/ecCodes+Home)
- [Pillow](https://pillow.readthedocs.io/en/stable/) for image generation
- [PyOpenCL](https://mathema.tician.de/software/pyopencl/) for GPU-accelerated processing of data and images
- [FFmpeg](https://www.ffmpeg.org/) for converting image sequences to video
