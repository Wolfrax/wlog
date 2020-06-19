DynDNS
******

:date: 2020-01-11
:modified: 2020-01-11
:tags: DNS
:summary: A note dynamic DNS

I use the domain `viltstigen.se <viltstigen.se>`_ with the obvious subdomain `www.viltstigen.se <www.viltstigen.se>`_.
For this blog I have also included the subdomain `wlog <wlog.viltstigen.se>`_.

Both domains are registered at `Binero <https://www.binero.se/>`_.

I am also using Binero dynamic DNS service as I don't have a static by my ISP.
My router does not have a dynamic DNS client included.

To keep the dynamic WAN IP address of my router updated to Binero DNS I have added this to rpi1 crontab

.. code-block:: bash

    00 *    * * *   curl -n -d 'hostname=www.viltstigen.se' 'https://dyndns.binero.se/nic/update' >/dev/null 2>&1
    00 *    * * *   curl -n -d 'hostname=wlog.viltstigen.se' 'https://dyndns.binero.se/nic/update'>/dev/null 2>&1

The ``-n`` option assume that a ``~/.netrc`` exists in the home directory of the current user (pi).
Change permission by ``$ chmod go= ~/.netrc```
Content for ``.netrc``:

.. code-block:: bash

    machine dyndns.binero.se login mats.melander@gmail.com password XXX
    machine dyndns.binero.se login mats.melander@gmail.com password XXX

Using ``curl`` is inline with Binero documentation, running every hour. It will make a POST using the information after
the -d option. curl should return "good" or "nchg", but the crontab rows directs to /dev/null, so not visible in syslog.

Note Do not add a DSN record for ``www.viltstigen.se`` manually at Binero, if this is made the DynDNS will not work.
The curl command above will add the subdomain ``www`` to the domain ``viltstigen.se`` and then it will be visible in the
DNS table at Binero. Same thing for the subdomain ``wlog.viltstigen.se`` of course.

