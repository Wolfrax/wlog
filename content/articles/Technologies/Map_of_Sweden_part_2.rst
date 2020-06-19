Map of Sweden #2
****************

:date: 2020-01-28
:modified: 2020-01-28
:tags: D3, Maps
:summary: A note on making maps #2

In a previous post, I showed how to make a map of Sweden as a SVG object, derived from geometrical information,
using D3. Here, I will focus of collecting meteorological observations from `SMHI <https://opendata.smhi.se/apidocs/metobs/index.html>`_
and create a simple HTTP-server that will respond with the data when requested. This will be made through 2 simple
python scripts.

The scripts
===========
There are two python 3.x scripts doing the work

* **collector.py:** This script will traverse the SMHI REST API and store the data in JSON format in a file.
  I have automated this script running once per day through crontab.
* **emitter.py:** This script is implemented as a HTTP-server, running as a background daemon. When it receives a
  GET-request, it will read the JSON file, created by collector.py and respond to the client.

I am using tools to have the workings of **emitter.py**; `Flask <http://flask.pocoo.org/>`_,
`Gunicorn <https://gunicorn.org/>`_ and `Supervisor <http://supervisord.org/introduction.html>`_.
They will be described below, but first I will start with installing them into a Python virtual environment.
In **collector.py** I will use requests library to access the SMHI observations, this library needs to be installed as well.

Installation
++++++++++++
Assuming a "clean" raspberry pi in target (in my case named **rpi2**) do as below.
This will install **pip**, **virtualenv**, **virtualenwrapper**, **autoenv** and **supervisor** systemwide.
Following that I create the virtual environment clover using python3. **requests**, **flask** and **gunicorn** are
installed into the virtual environment, thus not system wide.

.. code-block:: bash

    $ sudo apt-get update
    $ sudo apt-get install python-setuptools
    $ sudo easy_install pip
    $ sudo pip install virtualenv
    $ sudo pip install virtualenvwrapper
    $ sudo pip install autoenv
    $ sudo apt-get install supervisor
    $ mkvirtualenv --python=/usr/bin/python3 clover
    $ workon clover
    (clover) $ pip3 install requests
    (clover) $ pip3 install flask
    (clover) $ pip3 install gunicorn

Now everything should be installed.

SMHI meteorological observations
================================
Time to find out how we access the meteorological observations.
This is how it is described by SMHI

    The service is constructed as a REST API for easy access. The Entry point is located at
    https://opendata-download-metobs.smhi.se/api. From here a client can traverse down by following links through
    the levels until a specific data resource is available.

The **collector.py** script use http://opendata-download-metobs.smhi.se/api.json as the starting point to access
observations. SMHI expose data in 3 different formats: 1) JSON 2) XML 3) CSV, I will only care about JSON.

There is a multitude of observations that can be accessed, for my purpose a subset of these will do:

* **Temp:** Momentary value of air temperature, updated once per hour
* **Average temp:** Average air temperature for 1 day (24 h), at 00:00
* **Rain:** Sum once per day, at 06:00
* **Relative humidity:** Momentary value, once per hour
* **Snow depth:** Momentary value, once per hour
* **Air pressure:** At sea level, momentary value, once per hour
* **Lowest cloud layer:** Momentary value, once per hour

I also collect **Wind Direction** and **Wind Speed** (average values over 10 min, once per hour) but these values are not used.

A Jupyter notebook is available `here <https://github.com/Wolfrax/clover/tree/master/blog/Part%202>`__ to show a
simple interaction.

For each data set, there are some meta-data available, such as:

* **Latitude and Longitude** for each station
* **Name** of station
* **Active**, some stations might be inactive
* **Update**, when the data was updated

All of above is collected together with the value of the observation into a structure by the collector script.

**Note this** The stations will be different for each observation, e.g. the number of stations where rain observations
are available is larger than the number of stations for the air pressure observations. Therefore, we need to traverse
the API once per requested observation. To make the collector script somewhat more efficient it creates thread for
each observation so that the procedure is parallelized.

The final result is stored in the file **weather.js**.

The **collector.py** script is executed once per day using crontab. The entry in crontab is

.. code-block:: bash

    00 1    * * *   pi      /usr/bin/python3 /home/pi/app/clover/py/collector.py >> /var/log/clover.log 2>&1

Note that the script is executed as user "pi" and that any printout from the script is collected into
``/var/log/clover.log``. Ensure that the **collector.py** script have execution attribute set, that the
**clover.log** file exist in **/var/log** and is possible to write into. Use **chmod** and **chown** commands to do this.

The collector.py is short, not very complicated and available `here <https://github.com/Wolfrax/clover/blob/master/py/collector.py>`__ on GitHub.
The net result is a file, **weather.js**, in JSON format. The file name is hardcoded in the script as
**../data/weather.js**.

The beginning of the file looks like this

.. code-block:: bash

    {
        "date": "2019-03-07",
        "temp": [{
            "station": "Abisko",
            "updated": 1551985200000,
            "lon": 18.816546,
            "lat": 68.354122,
            "active": true,
            "val": -15.5
        }, {
    ...
    }

The full file includes all stations for key temp. Other keys in the file are

* **avg_temp**
* **wind_dir** (not used)
* **wind_speed** (not used)
* **rain**
* **rel_moisture** (humidity)
* **snow_depth**
* **pressure**
* **lowest_cloud**

The javascript that is accessing the data must use the exact key names shown above.

Emitter
=======
The last script to explain is **emitter.py**. This script is really short, the purpose of the script is to listen on
for HTTP GET-requests on the URI **/clover_data**, read the **weather.js** file and return the content to the HTTP client.
It is doing this through **Gunicorn** and **Flask**. The rationale for doing it this way is my local infrastructure
of raspberries.

My domain is https://www.viltstigen.se, and I have one raspberry (**rpi1**) as HTTP server listening on port 80 and 443.
The collector script is executing on another raspberry (**rpi2**) upstream of **rpi1**.
The way to implement this is to use `nginx <https://nginx.org/en/>`_ as HTTP and proxy server on both **rpi1** and **rpi2**.

I need to configure nginx on **rpi1** to distribute requests to clover to **rpi2**.

.. code-block:: nginx

    location /clover {
        try_files $uri $uri/ $uri/index.html $uri.html @clover;
    }

    location @clover {
        # proxy_pass http://rpi2.local; Note, a static IP address makes nginx more robust in case rpi1 is not running
        proxy_pass http://192.168.1.51;
        proxy_redirect     off;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host $server_name;
        proxy_read_timeout 300;
    }

    location /clover_data {
        try_files $uri $uri/ $uri/index.html $uri.html @clover_data;
    }

    location @clover_data {
        # proxy_pass http://rpi2.local; Note, a static IP address makes nginx more robust in case rpi1 is not running
        proxy_pass http://192.168.1.51:8096;
        proxy_redirect     off;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host $server_name;
        proxy_read_timeout 300;
    }

When a HTTP client access the URI https://www.viltstigen.se/clover, **rpi1** will pass this to **rpi2**.
Similar, if a client access https://www.viltstigen.se/clover_data, **rpi1** will pass the request upstream to **rpi2** on
port 8096. As my raspberries is protected by the uncomplicated firewall (ufw), the ports on **rpi2** needs to be configured
to allow the traffic through these commands

.. code-block:: bash

    $ sudo ufw allow from 192.168.1.0/24 to any port 8096
    $ sudo ufw allow from 192.168.1.0/24 to any port 80

Now an external HTTP-client can access **rpi2** through **rpi1**.

On **rpi2** a WSGI server is listening on port 8096 and executing a Flask application in the emitter script.
As the WSGI server is running as a daemon I use supervisor to control this. Supervisor is configured in the file
**clover_gunicorn.conf** (softlinked from **/etc/supervisor/conf.d** directory), the content looks like this

.. code-block:: bash

    [program:clover_gunicorn]
    command = /home/pi/.virtualenvs/clover/bin/gunicorn -b :8096 --reload emitter:app
    directory = /home/pi/app/clover/py
    user = root
    autostart = true
    autorestart = true
    startretries=3
    stdout_logfile = /var/log/supervisor/clover_gunicorn.log
    stderr_logfile = /var/log/supervisor/clover_gunicorn.err

This tells supervisor to execute gunicorn, bind it to port 8096 executing the Flask application "app" in module
"emitter". It will automatically reload the Flask application if any changes are made.

Finally, the core of the Flask application is (the actual script includes more error handling than shown below)

.. code-block:: python

    #!/usr/bin/env python

    from flask import Flask
    from flask import jsonify
    import json

    app = Flask(__name__)

    @app.route("/clover_data")
    def get_data():
        name = "/var/local/clover_weather.js"  # Hardcoded filename
        with open(name, 'r') as json_file:
            return json.dumps(json.load(json_file))

    if __name__ == "__main__":
        app.run(host='0.0.0.0', debug=True)

Above tells us that the Flask application will respond to the URI **/clover_data** by reading the file
**/var/local/clover_weather.js** (which I have symlinked to the actual file weather.js) and returning the content as a
JSON formatted string. Flask is running in debug mode, in case I would like to use this debug mode,
I issue these commands:

.. code-block:: bash

    $ export FLASK_APP=emitter.py
    $ export FLASK_DEBUG=1
    $ flask run --host=0.0.0.0 --port=8096

and access the URI https://rpi2.local:8096/clover_data from a web browser.