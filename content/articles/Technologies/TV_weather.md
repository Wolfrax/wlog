Title: Trafikverket weather station
Author: Mats Melander
Date: 2020-10-07
Modified: 2021-09-12
Tags: Python, weather
Category: Technologies
Summary: How to read and plot weather information by Trafikverket

# Introduction

In Sweden, Trafikverket (Swedish Transport Administration) have a 
[country wide network of weather stations](https://www.trafikverket.se/tjanster/trafiktjanster/VViS/) monitor
road conditions. The primary purpose is to use data for managing of roads, but data is available through
an [Open API](https://api.trafikinfo.trafikverket.se/).

I have [implemented](https://github.com/Wolfrax/tv) reading data from selected station recurrently (when new data is 
produced), store into a JSON file and generate an HTML-file. The implementation store and plot 
24 hours of data at most.

As an example, weather data for station "Lund N" is [here](https://www.viltstigen.se/tv_ws?stn=Lund)

# Implementation
Using the Open API require an authorization key, a [registration](https://api.trafikinfo.trafikverket.se/Account/Register)
is needed (free of charge). The key is available there.
The key is added to file `auth.yml` using syntax:

    auth:
        key: 71fa8aa80d...

The python program will read the key from this file.

To get the data, a query-string is needed, following the syntax as stated by Trafikverket.
Something like this.

```text
<REQUEST>
  <LOGIN authenticationkey='71fa8aa80d...'/>
  <QUERY sseurl="true" objecttype='WeatherMeasurepoint' schemaversion='1'>
    <INCLUDE>Observation.Sample</INCLUDE>  
    <INCLUDE>Observation.Air.RelativeHumidity.Value</INCLUDE>
    <INCLUDE>Observation.Air.Temperature.Value</INCLUDE>
    <INCLUDE>Observation.Wind.Direction.Value</INCLUDE>
    <INCLUDE>Observation.Wind.Speed.Value</INCLUDE>
    <INCLUDE>Observation.Aggregated10minutes.Precipitation.TotalWaterEquivalent.Value</INCLUDE>
    <INCLUDE>Observation.Aggregated30minutes.Wind.SpeedMax.Value</INCLUDE>
    <INCLUDE>Name</INCLUDE>
    <FILTER>
        <EQ name="Name" value='""" + stn_name + """' />
    </FILTER>
  </QUERY>
</REQUEST>
```
Any station available can be read by using its name, refer to this [map](https://www.trafikverket.se/trafikinformation/vag/?TrafficType=personalTraffic&map=1%2F606442.17%2F6886316.22%2F&Layers=RoadWeather%2b)
and zoom in to find the right name and use this in the `<FILTER>` paragraph.

The implementation starts with making a HTTP-GET request for json-formatted information:

```python
url = "https://api.trafikinfo.trafikverket.se/v2/data.json"
r = requests.post(url, data=query.encode('utf-8'), headers={'Content-Type': 'text/xml'}).json()
```
The response will include a `sse_url`, this can be used as:

```python
sse_url = r['RESPONSE']['RESULT'][0]['INFO']['SSEURL']
messages = SSEClient(sse_url)
try:
    for msg in messages:
    # more code here
    # ...
except ConnectionResetError:
    url = sse_url + "&lasteventid=" + msg.id
    messages = SSEClient(url)
```

Exception handling is needed as the connection to the server will go up and down. To continue reading from the same stream
the parameter `lasteventid` need to have the value in `msg.id` from the last received message.

The for-loop to get messages is contained in a `while True`-loop that includes the exception handling. Thus we have fixed
a robust connection toward Trafikverket. This has implication for the plotting, described below.

What Trafikverket implemented is so called [Server Side Events (SSE)](https://en.wikipedia.org/wiki/Server-sent_events).
This means that the server push notification on the connection when data is available, the client doesn't have to
recurrently poll the server. Thus, most of the time the implementation is stuck in the `for msg in message` statement.

When data  is available, we pick it up by
```python
data = json.loads(msg.data)
```
Following that, the data can be processed, for exampled plotted, this is described below.

# UI

Using [Flask](https://flask.palletsprojects.com/en/2.0.x/), [Highcharts](https://www.highcharts.com/), 
[Bootstrap](https://getbootstrap.com/), [jQuery](https://jquery.com/) and some javascript a web client/server model is 
used to expose information as a dahsboard.

The flask app is served through [gunicorn](https://gunicorn.org/) listening on port 8300 (using a systemd service).
A webclient uses a querystring parameter `stn` to indicate which station data to use, e.g. `stn=Lund`.

The flask-app (ws_emitter) generates an html-page in return, using the template mechanism with flask, see details at
[github](https://github.com/Wolfrax/tv).

The html-page uses bootstrap for layout of the dashboard, specifically using the grid system and card-component.
In the html code, id-values are used to set symbolic names of specific divisions of the page. These divisions are then
referenced by javascript code with actual data read from the server using ajax.

To render the table of the last hour of data, the jquery plugin [datatables](https://datatables.net/) is used. 
The querystring paramter `ind` (short for index) is used with value `-7`, indicating to get the last 7 values from the 
server (as reading are done normally every 10th minute from trafikverket, using the last 7 readings will get the last 
hour of data).

Highcharts are used to draw graphs of temperature and humidity (dual y-axis as the graphs are in the same diagram), rain
(also dual y-axis as both momentary and accumulated values are show in the same diagram), wind (using the specific 
wind-barb feature in Highcharts) and a wind-rose.

The wind-rose needs some calculations and is therefore using [d3.js](https://d3js.org/) `bin` function (normally used
for making histrograms) to group wind data in wind speed intervals. These bins are then looped to calculate the
frequency of wind-directions in certain intervals (0-45, 45 - 90, etc). This information are then fed into highcharts
windrose chart.

Better read the source code for all details of above...

## Daemon
The script runs as a daemon on a Raspberry Pi, to have this `systemd` is used and a service description file with
content below is stored in `/etc/systemd/system/tv_ws.service`:

```text
[Unit]
Description=Trafikverket weatherstation
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/pi/app/tv
User=pi
Group=www-data
ExecStart=/home/pi/app/tv/.venv/bin/python ws.py
Restart=always

[Install]
WantedBy=multi-user.target
```
