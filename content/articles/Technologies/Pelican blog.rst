Pelican blog
************

:date: 2020-01-12
:modified: 2020-05-01
:tags: Blog, Pelican
:summary: A note on setting Pelican for blogging

Using `Pelican <https://blog.getpelican.com/>`_  as blog software.
Follow installation instructions `here <https://docs.getpelican.com/en/stable/install.html>`_.

I use **rpi1**-node as front-end to external requests, but my production part of this blog resides on node **rpi2**.

Subdomain management
====================
I created a new subdomain to ``viltstigen.se`` called ``wlog.viltstigen.se`` at Binero. This was partly a necessity due
to my configuration and how Pelican works (by default).
Pelican uses relative paths of getting resources, e.g. ``/theme/css/admonition.css``, not absolute URL paths.
I use nginx as proxy on rpi1, where my DynDNS is pointing to. An HTTP request to ``wlog.viltstigen.se`` is directed
to this node. **rpi1** is configured (see nginx configuration below) to forward the request to **rpi2** where a nginx
web-server is running and will return requested resources through **rpi1**.

If I would have had the blog on, for example, ``www.viltstigen.se/blog/index.html`` (on my existing subdomain),
I could have configured nginx on rpi1 to forward all requests on the resource ``/blog/index.html`` to **rpi2**.
However all subsequent requests from the client would use paths relative to ``www.viltstigen.se`` and thus fail.

Example,  using **www** subdomain instead of **wlog**:

 **https://www.viltstigen.se/blog/index.html** would include the link
 **https://www.viltstigen.se/theme/css/elegant.prod.css**.
 As nginx would be configured to forward requests on **/blog/** to **rpi2** the subsequent resource request on
 **/theme/css/** would look locally at **rpi1** rather than forwarding to **rpi2**.

 Therefore, as I use the **wlog** subdomain, and forward all requests on this subdomain from **rpi1**
 to **rpi2**, the subsequent link in index.html is **https://wlog.viltstigen.se/theme/css/elegant.prod.css**.

As there is a new subdomain created, dynDNS at Binero needs to be updated accordingly, see
`DynDNS <{filename}/articles/Technologies/DynDNS.rst>`_.

Using SSL
=========
I want to enable `SSL <https://en.wikipedia.org/wiki/Transport_Layer_Security>`_ so that
`https <https://en.wikipedia.org/wiki/HTTPS>`_ can be used for my blog. A certificate is needed, for this purpose I use
`Let's Encrypt <https://letsencrypt.org/>`_. In the nginx configuration on **rpi1** HTTP-access is redirected to HTTPS.
The certificate is installed on rpi1. Below assumes that **Let's Encrypt** software is already installed.

.. code-block:: bash

    $ sudo ./letsencrypt-auto certonly -a webroot --webroot-path=/usr/share/nginx/html -d wlog.viltstigen.se
    /opt/eff.org/certbot/venv/local/lib/python2.7/site-packages/cryptography/hazmat/bindings/openssl/binding.py:163: CryptographyDeprecationWarning: OpenSSL version 1.0.1 is no longer supported by the OpenSSL project, please upgrade. The next version of cryptography will drop support for it.
      utils.CryptographyDeprecationWarning
    Saving debug log to /var/log/letsencrypt/letsencrypt.log
    Plugins selected: Authenticator webroot, Installer None
    Obtaining a new certificate
    Performing the following challenges:
    http-01 challenge for wlog.viltstigen.se
    Using the webroot path /usr/share/nginx/html for all unmatched domains.
    Waiting for verification...
    Cleaning up challenges

    IMPORTANT NOTES:
     - Congratulations! Your certificate and chain have been saved at:
       /etc/letsencrypt/live/wlog.viltstigen.se/fullchain.pem
       Your key file has been saved at:
       /etc/letsencrypt/live/wlog.viltstigen.se/privkey.pem
       Your cert will expire on 2020-03-29. To obtain a new or tweaked
       version of this certificate in the future, simply run
       letsencrypt-auto again. To non-interactively renew *all* of your
       certificates, run "letsencrypt-auto renew"
     - If you like Certbot, please consider supporting our work by:

       Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
       Donating to EFF:                    https://eff.org/donate-le

Check auto-renewal of certificates by

.. code-block:: bash

    $ sudo /opt/letsencrypt/letsencrypt-auto renew
    /opt/eff.org/certbot/venv/local/lib/python2.7/site-packages/cryptography/hazmat/bindings/openssl/binding.py:163: CryptographyDeprecationWarning: OpenSSL version 1.0.1 is no longer supported by the OpenSSL project, please upgrade. The next version of cryptography will drop support for it.
      utils.CryptographyDeprecationWarning
    Saving debug log to /var/log/letsencrypt/letsencrypt.log

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Processing /etc/letsencrypt/renewal/wlog.viltstigen.se.conf
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Cert not yet due for renewal

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Processing /etc/letsencrypt/renewal/www.viltstigen.se.conf
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Cert not yet due for renewal

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    The following certs are not due for renewal yet:
      /etc/letsencrypt/live/wlog.viltstigen.se/fullchain.pem expires on 2020-03-29 (skipped)
      /etc/letsencrypt/live/www.viltstigen.se/fullchain.pem expires on 2020-03-29 (skipped)
    No renewals were attempted.
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

In crontab on **rpi1**, auto renenwal is executing by these lines

.. code-block:: bash

    30 2    * * 1   root    /opt/letsencrypt/letsencrypt-auto renew >> /var/log/le-renew.log
    35 2    * * 1   root    /bin/systemctl reload nginx

nginx configuration
===================
In ``/etc/nginx/sites-enabled/wolfrax.conf`` on **rpi1** add these sections

.. code-block:: nginx

    server {
        listen 80;
        listen [::]:80;

        server_name wlog.viltstigen.se;

        # This will redirect http traffic to server below using https
        return 301 https://$server_name$request_uri;
    }

    server {
        # Reverse proxy to rpi2.local (192.168.1.51)
        listen 443 ssl;
        listen [::]:443 ssl;

        server_name wlog.viltstigen.se;

        # SSL configuration
        include snippets/ssl-wlog.viltstigen.se.conf;
        include snippets/ssl-params.conf;

        location / {
            proxy_pass http://192.168.1.51; # rpi2.local
        }

        location /.well-known/ {}  # do not redirect for this directory, used by letsencrypt
    }

Note the last row for **location /.well-known/**, this exclude the directory ".well-known" which is used by
**letsencrypt** when renewing the cerificate. (letsencrypt stores information in this directory when renewing the
certificate, hence we should not move requests upstreams or the renewal will fail).

In snippets-directory on **rpi1** add file ``ssl-wlog-viltstigen.se.conf`` with this content

.. code-block:: nginx

    ssl_certificate /etc/letsencrypt/live/wlog.viltstigen.se/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/wlog.viltstigen.se/privkey.pem;

No need to update "ssl-params.conf" file on **rpi1**.

Softlink the file (as I use a separate directory structure for my nginx files)

.. code-block:: bash

    $ sudo ln -s /home/pi/rpi1/etc/nginx/snippets/ssl-wlog.viltstigen.se.conf /etc/nginx/snippets/ssl-wlog.viltstigen.se.conf

Check nginx and restart

.. code-block:: bash

    $ sudo nginx -t
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful
    $ sudo systemctl restart nginx


On **rpi2**, create a new file ``wolfrax.conf`` with this content (``/clover/`` is used for another web application, not
connected to Pelican blog, on **rpi2**).

.. code-block:: nginx

    server {
        listen 80 default_server;
        listen [::]:80 default_server;

        root /var/www/html;

        index index.html index.htm index.nginx-debian.html;

        server_name _;

        location / {
            # First attempt to serve request as file, then
            # as directory, then fall back to displaying a 404.
            root /home/pi/app/wlog/;
            try_files $uri $uri/ =404;
        }

        location /clover/ {
            # First attempt to serve request as file, then
            # as directory, then fall back to displaying a 404.
            root /var/www/html/;
            try_files $uri $uri/ =404;
        }
    }

Using the files in the RPi-project, soft link files

.. code-block:: bash

    $ sudo mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf_OLD
    $ sudo rm /etc/nginx/sites-enabled/default  # Remove default config, softlinked from sites-available, if exists
    $ sudo ln -s /home/pi/rpi2/etc/nginx/nginx.conf /etc/nginx/nginx.conf
    $ sudo ln -s /home/pi/rpi2/etc/nginx/sites-enabled/wolfrax.conf /etc/nginx/sites-enabled/wolfrax.conf
    $ sudo nginx -t
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful
    $ sudo service nginx restart

Pelican themes
==============
To install pelican theme "elegant" clone the repo into the "themes" directory of pelican installation.
Below pelican theme "elegant" is installed into a virtual environment.

.. code-block:: bash

    $ git clone https://github.com/Pelican-Elegant/elegant /home/mm/dev/wlog/venv/lib/python3.8/site-packages/pelican/themes/elegant

Update Pelican settings, see below.

Pelican plugins
===============
Install all available plugins, specifically ``pelican-ipynb`` enabling using Jupyter notebooks.
Below pelican plugins are installed into a virtual environment.

.. code-block:: bash

    $ git clone --recursive https://github.com/getpelican/pelican-plugins /home/mm/dev/wlog/venv/lib/python3.8/site-packages/pelican/pelican-plugins

Then update ``pelicanconf.py``

.. code-block:: python

    PLUGIN_PATHS = PLUGIN_PATHS = ['/home/mm/dev/wlog/venv/lib/python3.8/site-packages/pelican/pelican-plugins']
    PLUGINS = ['liquid_tags.notebook', 'i18n_subsites']
    MARKUP = ('md', 'ipynb')
    IGNORE_FILES = ['.ipynb_checkpoints']

For ``pelican-ipynb`` this library needs to be installed:

.. code-block:: bash

    $ pip install pelican-jupyter

Pelican settings
================
Using a PyCharm project **wlog** for blog updates, create new directories under ``wlog/content/``:
'pdf', 'img', 'articles', 'pages'. Then update ``pelicanconf.py`` with

.. code-block:: python

    SOCIAL = (('Email', 'mats.melander@gmail.com'),
              ('Github', 'https://github.com/wolfrax'),)

    THEME = "elegant"

    ARTICLE_PATHS = ['articles']
    STATIC_PATHS = ['img', 'pdf', 'extra']
    PAGE_PATHS = ['pages']
    ARTICLE_URL = 'articles/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
    ARTICLE_SAVE_AS = 'articles/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
    PAGE_URL = 'pages/{slug}/'
    PAGE_SAVE_AS = 'pages/{slug}/index.html'
    CATEGORY_URL = 'category/{slug}'
    CATEGORY_SAVE_AS = 'category/{slug}/index.html'
    TAG_URL = 'tag/{slug}'
    TAG_SAVE_AS = 'tag/{slug}/index.html'
    EXTRA_PATH_METADATA = {
        'extra/robots.txt': {'path': 'robots.txt'},
        'extra/favicon.ico': {'path': 'favicon.ico'},
    }

Pelican commands
================
Using make, these commands

* ``make html`` and ``make serve``, will generate pages in ``output`` directory and then start a local server
  http://localhost:8000/
* ``make publish`` and ``make ssh_upload``, will generate for production and upload to the server (configured in Makefile)