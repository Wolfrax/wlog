Title: SMHI Meteorological observations
Author: Mats Melander
Date: 2020-07-05
Modified: 2020-07-11
Tags: GeoJSON, GIS, Open data
Category: Technologies
Summary: Collecting meteorological observations by SMHI and making it accessible

[SMHI](https://www.smhi.se/omsmhi) is publishing meteorological observations recurrently as open data, this is
accessible through a REST API, documented [here](https://opendata.smhi.se/apidocs/metobs/index.html).
The API is documented but not very accessible as you need to traverse several levels to reach the actual observations.

In order to simplify, and to make observations available in [GeoJSON](https://geojson.org/) format, I have created an
infrastructure that once per day reads all available observations, transform it into GeoJSON and store into files 
(one file per observation). Access to these files are made by generating web-pages and also through a simple web API.
This means that files can be downloaded, or read by accessing web URL's.

The main entry point to the web pages is [here](https://www.viltstigen.se/smhi_metobs/).

## Collecting observations
Once per day, at midnight, a Python script is executed (through crontab, using a Rapsberry Pi). This script traverse
the SMHI open data REST API for meteorological observations and store each observation series into a file with 
extension "geojson". As of now, there is normally 40 different types of observations available, the file created
have a descriptive name in Swedish. For example,
```text
01_Lufttemperatur__momentanvärde_1_gång_per_tim.geojson
```
The prefix in the file name is a unique 2 digit key, ranging from 01 and normally up to 40.

For each type of observation, SMHI has a number of stations distributed through out Sweden. The number of stations might
differ of each type of observation and might include stations that are not active. Further, some observations will have
stations with the same longitude/latitude values, thus making duplicates. The script handles duplicates and validate the
resulting GeoJSON file.

### Collector script
The full script is available [here](https://github.com/Wolfrax/smhi/blob/master/py/collector_metobs.py).

Multi threading, one thread per observation, is used to speed up sampling. The SMHI REST API is traversed and each 
observation is stored as one file. Each observation is stored as a GeoJSON feature, see below.
```python
point = geojson.Point((stn["longitude"], stn["latitude"]))
feature = geojson.Feature(geometry=point,
                          properties={"key": key["key"],
                                      "title": key['title'],
                                      "summary": key["summary"],
                                      "updated": stn["updated"],
                                      "timestamp": ts,
                                      "height": stn["height"],
                                      "value": val},
                          id=stn["name"])

```
The files, can be read using [Geopandas](https://geopandas.readthedocs.io/en/latest/index.html), as an example see
[this post]({filename}/articles/Technologies/carta_geoplot.md).
A couple of other files is created:

- **meta.json**, a file with some meta data about the collected observations, refer to the script for details
- **index.html**, a listing of all observation files generated, for example see [this](https://www.viltstigen.se/smhi_metobs2020/07/05/)
- **a root index.html** file, [link](https://www.viltstigen.se/smhi_metobs/)
- **latest** symbolic link in the root pointing to the latest generated files, see explanation below

The script is executed once per day by a crontab entry. **Note**, some observations are updated multiple times per day
by SMHI. As the collector script is executed only once per day, multiple updates will be missed.

### Directory structure
The files are stored into a hierarchy, below the root directory are (in order) year, month, day.
As an example:
```text
metobs/
       latest
       index.html
       2020/      
            07/  
               05/
                  01_xxx.geojson
                  meta.json
                  index.html
```
The root index.html file have sorted tables per year to navigate to the wanted observations for easy access.
In the root there is also a symbolic link "latest" that points to the last generated observations.

### Information
In the geojson file with observations, the general structure is:

- Latitude and Longitude as a Point object in `geometry` (using coordinate reference system WGS84)
- Station name in `id`
- `key`, unique 2 digit key for each type of observation
- A `title` for each observation
- A `summary` for each observation
- `updated` is a timestamp when the observation were made (in Unix EPOCH)
- `timestamp` is the same information as `updated` but as a readable string
- `height`, the height in meters above sea level for the station
- `value`, the actual observation value. Normally a figure, but sometime it is a coded value 
  (refer to [SMHI](https://opendata.smhi.se/apidocs/metobs/codes.html))

In the file `meta.json`, located in each observation directory, some meta data is accessible:

- **generated**, timestamp when the observation were collected and stored
- **resources**, number of observations collected
- **translations**, a record for each type of observation with these fields:
    * 2 digit string starting with "01", unique for each observation
    * resource: record with these fields
        * key: 2 digit string, starting with "01", unique for each observation
        * title: string, type of observation, for example "Lufttemperatur" (Air temperature)
        * summary: string, description of observation, typically how often
        * link: string, URL to SMHI open data where the latest observation can be collected

### Access
Access to observations can be made by interactively browse the [web pages](https://www.viltstigen.se/smhi_metobs/) and
downloading relevant files.

Programatically, the observations can be accessed using the URL `https://www.viltstigen.se/metobs` as a base.
Appending, in this order, &lt;year&gt;/&lt;month&gt;/&lt;day&gt;/&lt;filename&gt;, with `year, month, day` expressed 
in digits.

**Example**

    https://www.viltstigen.se/metobs/2020/07/06/02_Lufttemperatur__medelvärde_1_dygn_1_gång_per_dygn_kl_00.geojson
    
To simplify, as file names is long, wildcards are permitted.

**Example**

    https://www.viltstigen.se/metobs/2020/07/06/02*    

This will get the observation file starting with the key `02` which is unique.
Using a wildcard like `1*`, will access the first file starting with `1` in **sorted** order, ie the file with key `10`.

An additional simplification is to use `latest`.

**Example**

    https://www.viltstigen.se/metobs/latest/02*    

This will retrieve the latest observation starting with key `02`.

After the daily generation of new files (and new directory), a tarball - `metobs_data.tar.gz`is generated for backup
purposes (I copy this file to Google drive using rclone). If so wanted, this file can be downloaded so a private copy of
all information can be generated. Use this url 
[https://www.viltstigen.se/metobs/metobs_data.tar.gz](https://www.viltstigen.se/metobs/metobs_data.tar.gz)

A daily graphical weather map is maintained at 
[https://www.viltstigen.se/smhi_metobs/weather.html](https://www.viltstigen.se/smhi_metobs/weather.html).

