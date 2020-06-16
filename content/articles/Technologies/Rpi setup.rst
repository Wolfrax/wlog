Raspberry setup
***************

:date: 2020-01-05
:modified: 2020-02-09
:tags: Raspberry

Setup Raspbian
==============
Using `NOOBS <https://www.raspberrypi.org/downloads/noobs/>`_ to install
`Raspian <https://www.raspbian.org/RaspbianAbout>`_. A SD card (>= 16GB) is needed.

Download NOOBS and unzip it, then format the SD card. I use a MacBook, with the
application `"SDFormatter" <https://www.sdcard.org/downloads/index.html>`_, use the option "Overwrite Format"
(not "Quick Format"). When done, copy all files in the NOOBS root directory to the SD card, plug it into the Raspberry
and start it up. A self-explaining menu with OS'es to choose from appear.

Install Raspbian.

Once done, some configuration is needed to setup the environment to my liking.

Configure
=========
Note that below, at least some of it, can also be made through the Raspberry UI (Gnome).

bashrc
######
The bash-shell reads ``/etc/profile`` which in turn reads ``/etc/bash.bashrc``. These are the system-wide files.
Add this:

.. code-block:: bash

    alias ll='ls -l --color=auto'
    alias la='ls -A --color=auto'
    alias l='ls -CF --color=auto'
    alias ls='ls -l --color=auto'

Reload by:

.. code-block:: bash

    $ source ~/.bashrc

hostname
########
Change the hostname to rpi1.

Edit ``/etc/hosts``, change last row which states ``127.0.1.1 raspberrypi`` to ``127.0.1.1 rpi1``.
Then edit ``/etc/hostname`` and add the wanted host name (rpi1).
Make it take effect:

.. code-block:: bash

    $ sudo /etc/init.d/hostname.sh
    $ sudo reboot

Timezone and Locale
###################
To update to correct timezone (use ``$ date`` to check), do ``$ sudo dpkg-reconfigure tzdata``

If you get ``-bash: warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)`` message at login then
do ``$ sudo dpkg-reconfigure locales``, make sure that "en_US.UTF-8" is selected.

Firewall (UFW)
##############
Use UFW (Uncomplicated Firewall) as firewall protection, a good summary is `here <https://www.digitalocean.com/community/tutorials/how-to-setup-a-firewall-with-ufw-on-an-ubuntu-and-debian-cloud-server>`_.
Some commands:

.. code-block:: bash

    $ sudo apt-get install ufw
    $ sudo ufw disable
    $ sudo ufw enable
    $ sudo ufw allow ssh                  # allow for ssh traffic on port 22, equivalent $ sudo ufw allow 22/tcp
    $ sudo ufw delete allow ssh           # Remove ssh traffic
    $ sudo sudo ufw allow www             # allow www traffic on port 80
    $ sudo ufw allow from 192.168.1.0/24  # allow all nodes on subnet 192.168.1.X
    $ sudo ufw reset                      # Reset everything

My setup on one Raspberry (there is a difference between each Raspberry Pi node, as I have different ports open for web
applications).

.. code-block:: bash

    $ sudo ufw allow from 192.168.1.0/24 to any port 80   # Web server, HTTP
    $ sudo ufw allow from 192.168.1.0/24 to any port 443  # Web server, HTTPS
    $ sudo ufw allow from 192.168.1.0/24 to any port 22   # SSH
    $ sudo ufw allow from 192.168.1.0/24 to any port 8094 # Web app
    $ sudo ufw allow from 192.168.1.0/24 to any port 8096 # Web app
    $ sudo ufw status
    Status: active

    To                         Action      From
    --                         ------      ----
    8094                       ALLOW       192.168.1.0/24
    80                         ALLOW       192.168.1.0/24
    443                        ALLOW       192.168.1.0/24
    22                         ALLOW       192.168.1.0/24
    8096                       ALLOW       192.168.1.0/24

Networking
##########
`netstat <https://en.wikipedia.org/wiki/Netstat>`_ used for displaying information on network connections. Example:

.. code-block:: bash

    $ sudo netstat --tcp --listening --programs --numeric
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
    tcp        0      0 0.0.0.0:8094            0.0.0.0:*               LISTEN      3525/python
    tcp        0      0 0.0.0.0:8096            0.0.0.0:*               LISTEN      4338/python3
    tcp        0      0 0.0.0.0:5900            0.0.0.0:*               LISTEN      373/vncserver-x11-c
    tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      11194/nginx: master
    tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      383/sshd
    tcp6       0      0 :::548                  :::*                    LISTEN      1458/afpd
    tcp6       0      0 :::5900                 :::*                    LISTEN      373/vncserver-x11-c
    tcp6       0      0 :::80                   :::*                    LISTEN      11194/nginx: master
    tcp6       0      0 :::22                   :::*                    LISTEN      383/sshd
    tcp6       0      0 ::1:4700                :::*                    LISTEN      1459/cnid_metad

To check DNS use `dig <https://en.wikipedia.org/wiki/Dig_(command)>`_ or
`nslookup <https://en.wikipedia.org/wiki/Nslookup>`_. Need to install ``dnsutils`` to use them. Example:

.. code-block:: bash

    $ sudo apt-get install dnsutils
    $ dig www.viltstigen.se

    ; <<>> DiG 9.9.5-9+deb8u15-Raspbian <<>> www.viltstigen.se
    ;; global options: +cmd
    ;; Got answer:
    ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 62736
    ;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

    ;; QUESTION SECTION:
    ;www.viltstigen.se.		IN	A

    ;; ANSWER SECTION:
    www.viltstigen.se.	120	IN	A	85.225.114.58

    ;; Query time: 31 msec
    ;; SERVER: 192.168.1.1#53(192.168.1.1)
    ;; WHEN: Mon Jan 06 14:24:52 CET 2020
    ;; MSG SIZE  rcvd: 51

    $ nslookup www.viltstigen.se
    Server:     192.168.1.1
    Address:    192.168.1.1#53

    Non-authoritative answer:
    Name:    www.viltstigen.se
    Address: 85.225.114.58

Make a raspberry visible in OSX finder, install ``netatalk`` ($ sudo apt-get install netatalk).

Automatic reboot after kernel crash
###################################
Edit ``/etc/sysctl.conf` and add ``kernel.panic = 10``.
This will make a reboot after 10 seconds delay after kernel panic crash. Make the changes take effect and check result
by

.. code-block:: bash

    $ sudo sysctl --system\
    $ sudo sysctl -a | grep kernel.panic # check
    kernel.panic = 10
    kernel.panic_on_oops = 0
    kernel.panic_on_rcu_stall = 0
    kernel.panic_on_warn = 0
    sysctl: reading key "net.ipv6.conf.all.stable_secret"
    sysctl: reading key "net.ipv6.conf.default.stable_secret"
    sysctl: reading key "net.ipv6.conf.eth0.stable_secret"
    sysctl: reading key "net.ipv6.conf.lo.stable_secret"
    sysctl: reading key "net.ipv6.conf.wlan0.stable_secret"

uptimerobot
###########
`Uptimerobot <https://uptimerobot.com/>`_ is a free service that checks the response time for web-sites,
it alerts through email.

Supervisor
##########
`Supervisor <http://supervisord.org/>`_ is a tool for monitoring daemons. Install and configure supervisor

.. code-block:: bash

    $ sudo apt-get install supervisor
    $ sudo supervisorctl status
    $ sudo supervisorctl reread # Restart supervisor to have it grab the changes
    $ sudo supervisorctl update

NGINX
#####

Install and start **nginx**

.. code-block:: bash

    $ sudo apt update
    $ sudo apt install nginx
    $ sudo /etc/init.d/nginx start
    $ sudo apt-get purge apache2  # Remove apache in case it is installed

When changing **nginx** configuration, test and restart.

.. code-block:: bash

    $ sudo nginx -t  # Test to check if configuration is Ok
    $ sudo systemctl restart nginx  # Update and restart