Title: Installing geopandas and geoplot on Raspberry Pi
Author: Mats Melander
Date: 2020-07-07
Modified: 2020-07-14
Tags: Linux, Raspberry, GIS
Category: Technologies
Summary: Installing geopandas and geoplot on Raspberry Pi running buster

Installing [geopandas](https://geopandas.readthedocs.io/en/latest/) and 
[geoplot](https://residentmario.github.io/geoplot/index.html) on a Raspberry Pi turned out not to be 
straight forward. Hence, I tried to resolve and install this manually. The details of the environment is:

```text
Raspberry Pi 3 Model B Rev 1.2, Linux version 4.19.118-v7+, Raspbian GNU/Linux 10 (buster)
```

Just installing geopandas and geoplot using pip fails due to the dependencies these packages have.

* geopandas requires **fiona, shapely, pandas, pyproj** (use `pip show geopandas`)
* geoplot requires: **geopandas, descartes, contextily, seaborn, pandas, mapclassify, matplotlib, cartopy**

Specifically, there is some underlying dependencies of libraries 
**[gdal](https://gdal.org/), [proj](https://proj.org/about.html)** that needs to be resolved before installing.

The following recipe worked for me:

- First install gdal and check version
```bash
    $ sudo apt-get install gdal-bin, libgdal-dev
    $ gdal-config --version
    2.4.0
```
- Install `proj` version 6.3.2 using a tmp-directory, first install sqlite3 that `proj` is using
```bash
$ sudo apt-get install sqlite3
$ mkdir tmp
$ cd tmp
$ wget https://download.osgeo.org/proj/proj-6.3.2.tar.gz
$ tar xvf proj-6.3.2.tar.gz 
$ cd proj-6.3.2
$ ./configure
$ make
$ sudo make install
$ sudo ldconfig
```
- Now install <code>[fiona](https://github.com/Toblerity/Fiona)</code> and 
  <code>[pyproj](http://pyproj4.github.io/pyproj/stable/)</code> version 1.9.6
```bash
$ pip install fiona
$ pip install pyproj==1.9.6
```
- Before we can install geoplot, the library <code>[libatlas](https://packages.debian.org/sid/libatlas-base-dev)</code>
  needs to be installed. Then try to install <code>[geopandas](https://geopandas.readthedocs.io/en/latest/)</code> and
  <code>[geoplot](https://residentmario.github.io/geoplot/index.html)</code>
- geopandas also depends on <code>[shapely](https://shapely.readthedocs.io/en/latest/)</code> and
  <code>[rtree](https://github.com/Toblerity/rtree)</code>. `rtree` installation is described below.
```bash
$ sudo apt-get install libatlas-base-dev
$ pip install geopandas
$ pip install geoplot
```
During my installation, I got error messages but the installation and setup still worked

To install `rtree` I had to build the underlying library [libspatialindex](https://libspatialindex.org/) from source.
Here is how (if cmake is not installed, use `apt-get install cmake`)
```bash
$ mkdir libspatialindex
$ cd libspatialindex/
$ wget https://github.com/libspatialindex/libspatialindex/releases/download/1.9.3/spatialindex-src-1.9.3.tar.gz
$ tar -xvf spatialindex-src-1.9.3.tar.gz
$ cd spatialindex-src-1.9.3/
$ cmake -DCMAKE_INSTALL_PREFIX=/usr/local .
$ make
$ sudo make install
$ sudo ldconfig
$ pip install rtree
```