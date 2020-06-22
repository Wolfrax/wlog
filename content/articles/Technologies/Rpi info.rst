Raspberry information
*********************

:date: 2020-01-14
:modified: 2020-06-22
:tags: Raspberry
:summary: A note on getting information on Raspberry Pi's

As I have several active raspberries in my home location, I tend to forget the details of them.
For example, raspberry model, linux kernel version etc etc
So I decided to write a script to collect this and expose it in a simple, crude tabular form at my home page.
Here is how it is done.


Configuration
=============
I have (currently) 5 raspberries in various models. They are named "rpi1"..."rpi5" and have been assigned static
IP-addresses (192.168.1.50 to 192.168.1.54).

The rpi1-node is running my web-server (nginx), collects information from the other raspberries and expose the result
by generating a web-page using flask.

Raspberry configuration
=======================
Each raspberry is running a small python info-script, listening and responding on port 8094.
All raspberries are protected with the "uncomplicated firewall" (UFW).
To allow traffic on port 8094 do ``$ sudo ufw allow from 192.168.1.0/24 to any port 8094``, this will enable any type of
traffic (TCP/UDP) from any node on the 192.168.1 network, others are blocked.

Information to collect
======================
I want to collect and present the following information for each raspberry

* The host name and ip address
* Uptime and average load
* Raspberry model name
* Linux and raspbian versions
* CPU information
* Applications running on the raspberry

Above is possible to read from various files in raspbian. Let's go through this.
In rasbian (or more generally, in Linux) the kernel maintains a directory tree under the root ``/proc`` where readable
(ie text) files are found. So, the following is true

* hostname can be read from ``/proc/sys/kernel/hostname``
* uptime can be read from ``/proc/uptime``. Note that this file have 2 numbers, both expressed in seconds, the
  first number is seconds since restart, the second number is seconds in idle (which is not interesting for me).
  We will need to convert seconds into a timestring to make it more readable, this is shown later on.
* average load can be read from /proc/loadavg. Note that it is the first three numbers that is of interest, there are
  in total 5 numbers. See [1]_ for details
* raspberry model can be read from ``/proc/device-tree/model``.
* linux version is read from ``/proc/version``
* raspbian version is read from ``/etc/os-release``
* CPU information is read from ``/proc/cpuinfo``
* Applications running on the raspberry is not read but hardcoded into the script

Note that the information provided above needs to be formated to fit what I want.

Implementation
==============
Install flask, gunicorn and requests into the python virtual environment, below named "info".

.. code-block:: bash

    $ mkvirtualenv info
    $ pip install flask
    $ pip install gunicorn
    $ pip install requests

Or, using Python venv, creating ``.venv``, do

.. code-block:: bash

    $ python -m venv .venv
    $ source .venv/bin/activate
    (.venv) $ pip install flask
    (.venv) $ pip install gunicorn
    (.venv) $ pip install requests

I will be using `gunicorn <https://gunicorn.org/>`_ as the WSGI web-server,
`flask <http://flask.palletsprojects.com/en/1.1.x/>`_ as the web application (gunicorn receives HTTP requests and then
communicate with flask using WSGI calling convention). The flask application will act as a proxy and ask for information
from the other raspberries using requests, collect the information and return the information in JSON format to the
calling client.

Here is the main loop, comments below

.. code-block:: python

    app = Flask(__name__)

    @app.route("/info")
    def info():
        rpi = {'rpi1': format_info(get_info())}
        wait = 5.0

        try:
            rpi['rpi2'] = format_info(requests.get("http://rpi2.local:8094/info", timeout=wait).text)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            rpi['rpi2'] = {'name': 'rpi2 (Down)', 'apps': 'Down', 'uptime': 'Down', 'version': 'Down', 'cpu': 'Down'}

        try:
            rpi['rpi3'] = format_info(requests.get("http://rpi3.local:8094/info", timeout=wait).text)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            rpi['rpi3'] = {'name': 'rpi3 (Down)', 'apps': 'Down', 'uptime': 'Down', 'version': 'Down', 'cpu': 'Down'}

        try:
            rpi['rpi4'] = format_info(requests.get("http://rpi4.local:8094/info", timeout=wait).text)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            rpi['rpi4'] = {'name': 'rpi4 (Down)', 'apps': 'Down', 'uptime': 'Down', 'version': 'Down', 'cpu': 'Down'}

        try:
            rpi['rpi5'] = format_info(requests.get("http://rpi5.local:8094/info", timeout=wait).text)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            rpi['rpi5'] = {'name': 'rpi5 (Down)', 'apps': 'Down', 'uptime': 'Down', 'version': 'Down', 'cpu': 'Down'}

        return render_template("info.html", rpi=rpi)


    if __name__ == "__main__":
        app.run(host='0.0.0.0', debug=True)

The flask app is started with host parameter value as 0.0.0.0 which means that other hosts can reach this app.
Debugging is enabled.
To bind this flask application to gunicorn, using port 8094 the following configuration file (which I name
ìnfo_gunicorn.conf) exists.

.. code-block:: bash

    [program:info_gunicorn]
    command = /home/pi/.virtualenvs/info/bin/python /home/pi/.virtualenvs/info/bin/gunicorn -b :8094 --reload emitter:app
    directory = /home/pi/rpi1/info
    user = root
    autostart = true
    autorestart = true
    startretries=3
    stdout_logfile = /var/log/supervisor/info_gunicorn.log
    stderr_logfile = /var/log/supervisor/info_gunicorn.err

gunicorn and flask is running as a server on the rpi1 node and is supervised using http://supervisord.org/.
Check out the documentation to install this tool. The gunicorn configuration file should normally reside at
``/etc/supervisor/conf.d``, I have choosen to store this file elsewhere and provide a softlink from the conf.d
directory to the configuration file.

Finally, I have configured nginx with this location information

.. code-block:: nginx

    location /info {
        try_files $uri $uri/ $uri/index.html $uri.html @info;
    }

    location @info {
        # proxy_pass http://rpi1.local; Note, a static IP address makes nginx more robust in case rpi1 is not running
        proxy_pass http://192.168.1.50:8094;
        proxy_redirect     off;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host $server_name;
        proxy_read_timeout 300;
    }

In summary, a web client will ask for information using HTTP(S) connecting to nginx which will pass upstream to
gunicorn listening on port 8094, gunicorn will communicate with the flask application, which in turn will communicate
with the other raspberries, collect and format all information and return the result as HTML.

To have nginx reading the location information do $ sudo service nginx restart. You want to check (and correct) syntax
errors before restarting nginx using ``$ sudo nginx -t``.

In case you want to debug the flask application do this

.. code-block:: bash

    $ export FLASK_APP=emitter.py
    $ export FLASK_DEBUG=1
    $ flask run --host=0.0.0.0 --port=8094

Access the flask application in a web browser through http://rpi1.local:8094/info

The python script above calls the other raspberries using requests, like so

.. code-block:: python

    wait = 5.0

    try:
        rpi['rpi2'] = format_info(requests.get("http://rpi2.local:8094/info", timeout=wait).text)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        rpi['rpi2'] = {'name': 'rpi2 (Down)', 'apps': 'Down', 'uptime': 'Down', 'version': 'Down', 'cpu': 'Down'}

It will wait for 5.0 seconds before timing-out, assuming that the other raspberry is down and managing the exception.
The results are formated (format_info) and stored into a dictionary named rpi.
When the information has been collected, the flask function render_template is called with the rpi-dictionary as a
parameter.

The information is presented as a table with 5 rows and one column per raspberry. Therefore, in the script, I replace
``/n`` with HTML ``<br>`` and I use "?" as a marker in the information strings to know when to split into the 5 rows
(see the function format_info below).
The result is visible `here <https://www.viltstigen.se/info>`_.

Full listing
============
Here is the complete script running on rpi1 [2]_ followed by the flask template used (Note that I have hardcoded application information on row 4 in the get_info routine).

.. code-block:: python

    #!/usr/bin/env python

    from flask import Flask
    from flask import render_template
    from flask import Markup
    import datetime
    from subprocess import check_output


    __author__ = 'mm'
    app = Flask(__name__)


    def format_cpuinfo(s):
        print s
        no_of_cores = "No of cores: " + str(s.count("processor\\t:")) + "\\n\\n"
        model_name = s[s.find("model name"): s.find("BogoMIPS")] + "\\n"
        features = s[s.find("Features"): s.find("CPU implementer")] + "\\n"
        hardware = s[s.find("Hardware"):]
        print no_of_cores + model_name + features + hardware
        return no_of_cores + model_name + features + hardware


    def get_info():
        with open('/proc/sys/kernel/hostname', 'r') as f:
            inf = f.read().replace("\\n", " ") + \
                  "(" + check_output(['hostname', '--all-ip-addresses']).replace(" \\n", "") + ")" + "?"

        inf += "Weather, EMC, Info, Vilt, Swind, nginx" + "?"

        with open('/proc/uptime', 'r') as f:
            up_str = f.read()
        ti = int(float(up_str.split(" ")[0]))
        inf += str(datetime.timedelta(seconds=ti)) + "\\n"
        with open('/proc/loadavg', 'r') as f:
            load_str = f.read()
        load = load_str.split(" ")
        inf += load[0] + " " + load[1] + " " + load[2] + "?"

        with open('/proc/device-tree/model', 'r') as f:
            inf += f.read() + "\\n"
        with open('/proc/version', 'r') as f:
            vers = f.read()
            inf += vers[:vers.find("(")] + "\\n"
        with open('/etc/os-release', 'r') as f:
            vers = f.read()
            ind1 = vers.find('"') + 1
            ind2 = vers[ind1:].find('"') + ind1
            inf += vers[ind1:ind2] + "?"

        with open('/proc/cpuinfo', 'r') as f:
            s = f.read()
            inf += format_cpuinfo(s)

        return inf


    def format_info(inf):
        ret = {}
        inf_str = inf.replace("\\n", "<br>").split("?")
        ret['name'] = Markup(inf_str[0])
        ret['apps'] = Markup(inf_str[1])
        ret['uptime'] = Markup(inf_str[2])
        ret['version'] = Markup(inf_str[3])
        ret['cpu'] = Markup(inf_str[4])
        return ret


    @app.route("/info")
    def info():
        rpi = {'rpi1': format_info(get_info())}
        wait = 5.0

        try:
            rpi['rpi2'] = format_info(requests.get("http://rpi2.local:8094/info", timeout=wait).text)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            rpi['rpi2'] = {'name': 'rpi2 (Down)', 'apps': 'Down', 'uptime': 'Down', 'version': 'Down', 'cpu': 'Down'}

        try:
            rpi['rpi3'] = format_info(requests.get("http://rpi3.local:8094/info", timeout=wait).text)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            rpi['rpi3'] = {'name': 'rpi3 (Down)', 'apps': 'Down', 'uptime': 'Down', 'version': 'Down', 'cpu': 'Down'}

        try:
            rpi['rpi4'] = format_info(requests.get("http://rpi4.local:8094/info", timeout=wait).text)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            rpi['rpi4'] = {'name': 'rpi4 (Down)', 'apps': 'Down', 'uptime': 'Down', 'version': 'Down', 'cpu': 'Down'}

        try:
            rpi['rpi5'] = format_info(requests.get("http://rpi5.local:8094/info", timeout=wait).text)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            rpi['rpi5'] = {'name': 'rpi5 (Down)', 'apps': 'Down', 'uptime': 'Down', 'version': 'Down', 'cpu': 'Down'}

        return render_template("info.html", rpi=rpi)


    if __name__ == "__main__":
        app.run(host='0.0.0.0', debug=True)

HTML template

.. code-block:: html

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Raspberry info</title>
        <style>
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
            }
        </style>
    </head>
    <body>
    <table style="width:100%">
        <tr>
            <th></th>
            <th>{{ rpi.rpi1.name }}</th>
            <th>{{ rpi.rpi2.name }}</th>
            <th>{{ rpi.rpi3.name }}</th>
            <th>{{ rpi.rpi4.name }}</th>
            <th>{{ rpi.rpi5.name }}</th>
        </tr>
        <tr>
            <th>Running</th>
            <td>{{ rpi.rpi1.apps }}</td>
            <td>{{ rpi.rpi2.apps }}</td>
            <td>{{ rpi.rpi3.apps }}</td>
            <td>{{ rpi.rpi4.apps }}</td>
            <td>{{ rpi.rpi5.apps }}</td>
        </tr>
        <tr>
            <th>Uptime</th>
            <td>{{ rpi.rpi1.uptime }}</td>
            <td>{{ rpi.rpi2.uptime }}</td>
            <td>{{ rpi.rpi3.uptime }}</td>
            <td>{{ rpi.rpi4.uptime }}</td>
            <td>{{ rpi.rpi5.uptime }}</td>
        </tr>
        <tr>
            <th>Version</th>
            <td>{{ rpi.rpi1.version }}</td>
            <td>{{ rpi.rpi2.version }}</td>
            <td>{{ rpi.rpi3.version }}</td>
            <td>{{ rpi.rpi4.version }}</td>
            <td>{{ rpi.rpi5.version }}</td>
        </tr>
        <tr>
            <th>CPU</th>
            <td valign="top">{{ rpi.rpi1.cpu }}</td>
            <td valign="top">{{ rpi.rpi2.cpu }}</td>
            <td valign="top">{{ rpi.rpi3.cpu }}</td>
            <td valign="top">{{ rpi.rpi4.cpu }}</td>
            <td valign="top">{{ rpi.rpi5.cpu }}</td>
        </tr>
    </table>
    <br>
    <a href="https://elinux.org/RPi_HardwareHistory">RPi HardwareHistory</a>
    <br>
    <a href="https://unix.stackexchange.com/questions/43539/what-do-the-flags-in-proc-cpuinfo-mean">CPU Info</a>
    <br>
    <br>
    Copyright (C) Mats Melander
    </body>
    </html>

The python scripts executing (and listening on port 8094 [3]_) on the other raspberries is a simple copy of the rpi1
functions format_cpuinfo and get_info, like so (the same virtual environment, supervisor etc is installed per raspberry).

.. code-block:: python

    #!/usr/bin/env python

    from flask import Flask
    import datetime
    from subprocess import check_output


    __author__ = 'mm'
    app = Flask(__name__)


    def format_cpuinfo(s):
        print s
        no_of_cores = "No of cores: " + str(s.count("processor\\t:")) + "\\n\\n"
        model_name = s[s.find("model name"): s.find("BogoMIPS")] + "\\n"
        features = s[s.find("Features"): s.find("CPU implementer")] + "\\n"
        hardware = s[s.find("Hardware"):]
        print no_of_cores + model_name + features + hardware
        return no_of_cores + model_name + features + hardware


    def get_info():
        with open('/proc/sys/kernel/hostname', 'r') as f:
            # NB! on Python 3, check_output needs to be decoded before replace (it returns byte)
            #  check _output(['hostname', '--all-ip-addresses']).decode().replace(" \\n", "")
            inf = f.read().replace("\\n", " ") + \
                  "(" + check_output(['hostname', '--all-ip-addresses']).replace(" \\n", "") + ") ?"

        inf += "Blog" + "?"

        with open('/proc/uptime', 'r') as f:
            up_str = f.read()
        ti = int(float(up_str.split(" ")[0]))
        inf += str(datetime.timedelta(seconds=ti)) + "\\n"
        with open('/proc/loadavg', 'r') as f:
            load_str = f.read()
        load = load_str.split(" ")
        inf += load[0] + " " + load[1] + " " + load[2] + "?"

        with open('/proc/device-tree/model', 'r') as f:
            inf += f.read() + "\\n"
        with open('/proc/version', 'r') as f:
            vers = f.read()
            inf += vers[:vers.find("(")] + "\\n"
        with open('/etc/os-release', 'r') as f:
            vers = f.read()
            ind1 = vers.find('"') + 1
            ind2 = vers[ind1:].find('"') + ind1
            inf += vers[ind1:ind2] + "?"

        with open('/proc/cpuinfo', 'r') as f:
            s = f.read()
            inf += format_cpuinfo(s)

        return inf


    @app.route("/info")
    def info():
        return get_info()


    if __name__ == "__main__":
        app.run(host='0.0.0.0', debug=True)

.. [1] The first three fields in this file are load average figures giving the number of jobs in the run queue (state R) or
       waiting for disk I/O (state D) averaged over 1, 5, and 15 minutes. They are the same as the load average numbers given
       by uptime(1) and other programs.
       The fourth field consists of two numbers separated by a slash (/). The first of these is the number of currently
       executing kernel scheduling entities (processes, threads); this will be less than or equal to the number of CPUs.
       The value after the slash is the number of kernel scheduling entities that currently exist on the system.
       The fifth field is the PID of the process that was most recently created on the system.

.. [2] The extraction of information and formatting is pretty crude, not my proudest moment... ↩︎

.. [3] I use Uncomplicated Firewall (UFW), so this needs to be configured to allow traffic on this port, for example
       ``sudo ufw allow from 192.168.1.0/24 to any port 8094``
