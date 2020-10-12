Title: Trafikverket weather station
Author: Mats Melander
Date: 2020-10-07
Modified: 2020-10-12
Tags: Python, weather
Category: Technologies
Summary: How to read and plot weather information by Trafikverket

# Introduction

In Sweden, Trafikverket (Swedish Transport Administration) have a 
[country wide network of weather stations](https://www.trafikverket.se/tjanster/trafiktjanster/VViS/) monitor
road conditions. The primary purpose is to use data for managing of roads, but data is available through
an [Open API](https://api.trafikinfo.trafikverket.se/).

I have [implemented](https://github.com/Wolfrax/tv) reading data from selected station recurrently (when new data is 
produced), store into a file and generates some plots as png-files and an HTML-file. The implementation store and plot 
24 hours of data at most.

As an example, weather data for station "Lund N" is [here](https://www.viltstigen.se/tv_ws/)

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
  <QUERY sseurl="true" objecttype='WeatherStation' schemaversion='1'>
    <INCLUDE>Measurement.Air.RelativeHumidity</INCLUDE>
    <INCLUDE>Measurement.Air.Temp</INCLUDE>  
    <INCLUDE>Measurement.MeasureTime</INCLUDE>    
    <INCLUDE>Measurement.Precipitation.Amount</INCLUDE>
    <INCLUDE>Measurement.Precipitation.AmountName</INCLUDE>
    <INCLUDE>Measurement.Precipitation.Type</INCLUDE>
    <INCLUDE>Measurement.Wind.Direction</INCLUDE>
    <INCLUDE>Measurement.Wind.Force</INCLUDE>
    <INCLUDE>Measurement.Wind.ForceMax</INCLUDE>
    <INCLUDE>Name</INCLUDE>
    <FILTER>
        <EQ name="Name" value='Lund N' />
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
Following that, the data can be processed, for exampled plotted, thi is described below.

As the plotting is made within a loop (the outmost loop is the `while True` loop, and the inner loop is the
`for msg in messages`) we need to consider how memory is handled when plotting. In my case, I use maplotlib and figures,
subplots, axis etc needs to be explicitly closed before we plot next time in the loops.

There are several ways to do this of course, as an exercise I chose to start a new process each time a plot is generated.
This will free up any memory used by matplotlib when the process terminates. It might look as overkill (and probably is...)
but does the work, and, besides, plotting is normally made every 10:nth minute.

This snippet shows the process thing for plotting:
```python
p = Process(target=do_graph, args=(msr,))
p.start()
p.join(timeout=120)  # kill after 2 minutes
if p.exitcode is not None and p.exitcode < 0:
    logging.warning("Graphical process - exit on timeout, is_alive is {}".format(p.is_alive()))
    if p.is_alive(): p.kill()
```
A new process is created, executing the routine `do_graph` with argument `msr` (that includes data to be plotted).
The process needs to be explicitly started (`p.start()`), the we wait at most 120 seconds for it to terminate
(`p.join()`). If the join-statement timeout, ie something has gone wrong, we issue a warning and check if the process is
still alive. If it is, brutally kill it (`p.kill()`) .

Ok, now for plotting

# Plotting
I use [matplotlib](https://matplotlib.org/index.html), partly for training purposes for the 'normal' plots.
For windrose plotting, I use [python-windrose](https://github.com/python-windrose/windrose) for convenience.

As several plots have a time axis, I need to adjust matplotlibs timezone setting (in my case UTC+2:00 hours) or else
the plots will be wrongly adjusted.

```python
matplotlib.rcParams['timezone'] = '+2:00'
```
Using matplotlib, I create 2 figures. Figure 1 for plotting air temperature, humidity (in the same sub-plot), rain
(in a second sub-plot) and wind force/direction (sub-plot 3). 
Figure 2 is the windrose plot.

For figure 1, we do:
```python
temp_rain_fig = plt.figure(figsize=(10, 15))

ax1 = plt.subplot(3, 1, 1)
temp_rain_fig.add_axes(ax1)

ax2 = self.ax1.twinx()  # Create a right-hand y-axis
temp_rain_fig.add_axes(ax2)

ax3 = plt.subplot(3, 1, 2, sharex=ax1)  # Share x-axis with subplot 1
temp_rain_fig.add_axes(ax3)

ax4 = ax3.twinx()
temp_rain_fig.add_axes(ax4)

ax5 = plt.subplot(3, 1, 3, sharex=ax1)   # Share x-axis with subplot 1
temp_rain_fig.add_axes(ax5)
``` 
This figure (`temp_rain_fig`) have 3 subplots:

1. ax1, ax2: To plot temperature (y-axis to left) and humidity (y-axis on right)
2. ax3, ax4: To plot rain, both non-accumlated (y-axis to left) and accumulated (y-axis on right) 
3. ax5: To plot wind strength, both average and maximum as two graphs. To this graph, wind direction will be added

The last plot is generated into a separate figure. This is the windrose plot.
This comes with a separate library, [python-windrose](https://github.com/python-windrose/windrose).

```python
windrose_fig = plt.figure(figsize=(5, 5))
THETA_LABELS = ["E", "N-E", "N", "N-W", "W", "S-W", "S", "S-E"]
wr_ax = WindroseAxes.from_ax(fig=self.windrose_fig, theta_labels=THETA_LABELS)
windrose_fig.add_axes(wr_ax)
```

To get the labeling right for the windrose plot, `THETA_LABLES` needs to be explicitly added as above.
This seems to have changed over versions (I'm using version 1.6.8).

Before plotting, data is collected into lists, for example

```python
time = [dateutil.parser.parse(msr["MeasureTime"]) for msr in data]
temp = [msr["Air"]["Temp"] for msr in data]
ax1.plot(time, temp)
ax1.annotate(str(temp[0]), xy=(time[0], temp[0]))
ax1.annotate(str(temp[-1]), xy=(time[-1], temp[-1]))
```

The last 2 rows, annotates the graph at start and endpoints.

The windrose is made like this

```python
wr_ax.bar(wind_dir, wind_force, normed=True, opening=0.8, edgecolor='white')
```
For the plotting of wind direction and strength (in the oridnary plot, not windrose), this snippet is applicable:

```python
WIND_LABELS = ["N", "N-E", "E", "S-E", "S", "S-W" , "W", "N-W"]
WIND_DEGREES = [90, 45, 0, 315, 270, 225, 180, 135]
bins = numpy.linspace(0, 360, len(WIND_LABELS))
for i, v in enumerate(wind_dir_hour):
    bin = numpy.digitize(wind_dir_hour[i], bins)
    # bin can be out of index if "Direction" == "NaN"
    if bin < len(WIND_DEGREES):
        m = MarkerStyle(r'$\leftarrow$')
        m._transform.rotate_deg(WIND_DEGREES[bin])
        self.ax5.plot(wind_time_hour[i], wind_val_hour[i],
                      marker=m,
                      markersize=20,
                      linestyle='None', color='crimson')

for i, dir in enumerate(wind_dir_hour):
    bin = numpy.digitize(wind_dir_hour[i], bins)
    if bin < len(WIND_LABELS):
        self.ax5.annotate(WIND_LABELS[bin], (wind_time_hour[i], wind_val_hour[i]),
                          xytext=(0, -20), textcoords='offset points')
```
First, I divide the space 0 - 360 into 8 bins (length of WIND_LABELS), then I loop over a list of hourly wind directions
(a subset of all wind direction measurements) and catch into which bin each value goes into (bin).
Now, wind direction values might have the value 'NaN' in case I have prevously caught a strange or missing value (this happens).

On the graph for wind force, I want to indicate the wind direction, so I capture a lefthand arraw symbol as marker
(`r$\leftarrow$`) and rotate (`_transform.rotate`) this by looking up a value in WIND_DEGREES using the previous bin
value. Finally, I plot the rotated marker on ax5.

I also want to annotate the wind direction below the marker, which is the last part of above snippet.

To format the x-axis of the plots, I use this:

```python
hours = mdates.HourLocator(interval=1)
h_fmt = mdates.DateFormatter('%H:%M')
ax1.tick_params(axis='x', labelrotation=45)
ax5.xaxis.set_major_locator(hours)
ax5.xaxis.set_major_formatter(h_fmt)
```
Using this, I set the format "10:00", rotated 45 degrees, on each tick at the x-axis.

## Daemon
The script runs as a daemon on a Raspberry Pi, to have this `systemd` is used and a service description file with
content below is stored in `/etc/systemd/system/tv_ws.service`:

```text
[Unit]
Description=Trafikverket weatherstation
After=network.target

[Service]
# To enable this, systemctl needs to be done in the following order
#   $ sudo systemctl enable /home/pi/rpi5/etc/systemd/user/tv_ws.service
#   $ sudo systemctl start tv_ws.service
# The first (enable) command will create symlink and enable the service so it get started at reboot
#
Type=simple
WorkingDirectory=/home/pi/app/tv
User=pi
Group=www-data
ExecStart=/home/pi/app/tv/.venv/bin/python ws.py
Restart=always

[Install]
WantedBy=multi-user.target
```

An HTML file is generated by the script using Flask, the file make reference to the plots that is saved as PNG-files.

Refer to the full implementation [here](https://github.com/Wolfrax/tv)
