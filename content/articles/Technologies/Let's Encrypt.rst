Let's Encrypt
*************

:date: 2020-01-13
:modified: 2020-05-01
:tags: Raspberry, SSH, HTTPS

The recommended way for web traffic is to use HTTPS which requires a certificate.
There is a free certificate authority for this purpose, `Let's Encrypt <https://letsencrypt.org/>`_.

In this post I describe my configuration and how to automatically renew the certificate when expired.
The basic recipe (for Ubuntu 16-04) I followed is available
`here <https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04>`_,
another good description is this `gist <https://gist.github.com/cecilemuller/a26737699a7e70a7093d4dc115915de8>`_.

Environment
===========
I'm using nginx on **rpi1**, Raspberry Pi Model B Rev 2, running Linux version 4.1.13+ Raspbian GNU/Linux 8 (jessie).

The nginx server works as a proxy-server, redirecting web-application traffic to other raspberries behind this server.
My domain name is www.viltstigen.se.

Installation
============
Start by cloning the github letsencrypt repository.

.. code-block:: bash

    $ sudo git clone https://github.com/letsencrypt/letsencrypt /opt/letsencrypt

Using the domain name and nginx root directory (see Environment above) we issue the following commands

.. code-block:: bash

    $ cd /opt/letsencrypt
    $ sudo ./letsencrypt-auto certonly -a webroot --webroot-path=/usr/share/nginx/html -d www.viltstigen.se

The script will ask for some questions, be prepared to state email address and accept Terms of Service

I obtained the following response (I was running this 2017-06-26)

.. code-block:: bash

    Saving debug log to /var/log/letsencrypt/letsencrypt.log
    Obtaining a new certificate
    Performing the following challenges:
    http-01 challenge for www.viltstigen.se
    Using the webroot path /usr/share/nginx/html for all unmatched domains.
    Waiting for verification...
    Cleaning up challenges
    Generating key (2048 bits): /etc/letsencrypt/keys/0000_key-certbot.pem
    Creating CSR: /etc/letsencrypt/csr/0000_csr-certbot.pem

    IMPORTANT NOTES:
     - Congratulations! Your certificate and chain have been saved at
       /etc/letsencrypt/live/www.viltstigen.se/fullchain.pem. Your cert
       will expire on 2017-06-26. To obtain a new or tweaked version of
       this certificate in the future, simply run letsencrypt-auto again.
       To non-interactively renew *all* of your certificates, run
       "letsencrypt-auto renew"
     - If you like Certbot, please consider supporting our work by:

       Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
       Donating to EFF:                    https://eff.org/donate-le

Let's check the output

.. code-block:: bash

    $ sudo ls -l -R  /etc/letsencrypt/live/
    /etc/letsencrypt/live/:
    total 4\
    drwxr-xr-x 2 root root 4096 Mar 28 20:53 www.viltstigen.se

    /etc/letsencrypt/live/www.viltstigen.se:
    total 4
    lrwxrwxrwx 1 root root  41 Mar 28 20:53 cert.pem -> ../../archive/www.viltstigen.se/cert1.pem
    lrwxrwxrwx 1 root root  42 Mar 28 20:53 chain.pem -> ../../archive/www.viltstigen.se/chain1.pem
    lrwxrwxrwx 1 root root  46 Mar 28 20:53 fullchain.pem -> ../../archive/www.viltstigen.se/fullchain1.pem
    lrwxrwxrwx 1 root root  44 Mar 28 20:53 privkey.pem -> ../../archive/www.viltstigen.se/privkey1.pem
    -rw-r--r-- 1 root root 543 Mar 28 20:53 README

Next step is to generate a Diffie-Hellman group, this will take some time

.. code-block:: bash

    $ sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

The output is in the /etc/ssl/certs directory and the file is a container for the public certificate.
Now it's time to configure nginx

NGINX
=====
Let's first define how I have structured the configuration files for nginx.
The directory tree for nginx looks like this

.. code-block:: bash

    /etc/nginx
    ├── conf.d
    ├── sites-available
    ├── sites-enabled
    └── snippets

The basic configuration file is /etc/nginx/nginx.conf, which includes this row (among other)
``include /etc/nginx/sites-enabled/*;``. So all files in the sites-enabled directory is included by nginx.
Traditionally, you store configuration files in the ``sites-available`` directory, then softlink these files to
``sites-enabled`` for easy on/off switching.

So, I have created a configuration file ``/etc/nginx/sites-enabled/wolfrax.conf``.
This file defines 2 servers as follows

.. code-block:: nginx

    server {
        listen 80;
        listen [::]:80;

        server_name www.viltstigen.se;
        # This will redirect http traffic to server below using https
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        listen [::]:443 ssl;

        server_name www.viltstigen.se;

        root /usr/share/nginx/html;
        index index.html index.htm;

        # SSL configuration
        include snippets/ssl-www.viltstigen.se.conf;
        include snippets/ssl-params.conf;

        include snippets/locations.conf;
    }

Let's digest these definitions somewhat.

The 2 listen rows are for TCP/IP v4 and v6 respectively, listening on respective port numbers.

The last row on the first server (return 301 https://$server_name$request_uri;) is important in this context.
If the server is approached by a client using HTTP (port 80) it generates a 301-redirect response, this response tells
the client where to go (``https://$server_name$request_uri``) which is simply put the same URI as it first used but using
HTTPS instead of HTTP. Thus we enforce usage of HTTPS.

.. note:: If the target server is upstream and nginx is simply a proxy-pass function the location
          **.well-known** needs to be excluded to be upstreamed.
          See `Pelican blog <https://wlog.viltstigen.se/articles/2020/01/12/pelican-blog/>`_

The second server definition is receiving the HTTPS traffic and includes 3 snippet-files as indicated.

The first file, ``snippets/ssl-www.viltstigen.se.conf``, simply includes 2 rows

.. code-block:: nginx

    ssl_certificate /etc/letsencrypt/live/www.viltstigen.se/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.viltstigen.se/privkey.pem;

These files were generated previously

The second file (``snippets/ssl-params.conf``) have more information

.. code-block:: nginx

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
    ssl_ecdh_curve secp384r1;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    # Try to use Google (8.8.8.8) as resolver
    resolver 8.8.8.8 valid=300s;
    resolver_timeout 10s;
    # Disable preloading HSTS for now.  You can use the commented out header line that includes
    # the "preload" directive if you understand the implications.
    #add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload";
    add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;

For details on this configuration refer to Cipherli.st and Strong SSL Security on nginx

The third file ``snippets/locations.conf`` have several upstream locations, what is relevant in this context is this
part of the file

.. code-block:: nginx

    location /wolfblog {
        try_files $uri $uri/ $uri/index.html $uri.html @wolfblog;
    }

    location @wolfblog {
        # proxy_pass http://rpi2.local:2368; Note, a static IP address makes nginx more robust in case rpi3 is not running
        proxy_pass        http://192.168.1.51:2368;
        proxy_redirect    off;
        proxy_set_header  Host $host;
        proxy_set_header  X-Real-IP $remote_addr;
        proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header  X-Forwarded-Host $server_name;
    }


Note that if my domain (www.viltstigen.se) is accessed with this URI: ``https://www.viltstigen.se/wolfblog``,
the first section above kicks in. It tries, in order, to access any files stated in the URI, treat the URI as a
directory, access the file index.html in the URI location, and finally and file with extension "html" through the URI.
If nothing is found (the normal case) it upstreams to to the @wolfblog location that passes on to the rpi2 node on
port 2368 which has a static IP address of 192.168.1.52.

When nginx files have been update, verify the configuration and restart

.. code-block:: bash

    $ sudo nginx -t
    $ sudo systemctl restart nginx

Automatic renewal of certificate
================================
Certificates is valid during a finite time and hence needs to be renewed recurrently. We can do this manually through

.. code-block:: bash

    $ sudo /opt/letsencrypt/letsencrypt-auto renew

    Saving debug log to /var/log/letsencrypt/letsencrypt.log

    -------------------------------------------------------------------------------
    Processing /etc/letsencrypt/renewal/www.viltstigen.se.conf
    -------------------------------------------------------------------------------
    Cert not yet due for renewal

    The following certs are not due for renewal yet:
      /etc/letsencrypt/live/www.viltstigen.se/fullchain.pem (skipped)
    No renewals were attempted.

To do this automatically and recurrently, add the following lines into /etc/crontab

.. code-block:: bash

    30 2    * * 1   root    /opt/letsencrypt/letsencrypt-auto renew >> /var/log/le-renew.log
    35 2    * * 1   root    /bin/systemctl reload nginx

This will create a new cron job that will execute the letsencrypt-auto renew command every Monday at 2:30 am,
and reload nginx at 2:35am (so the renewed certificate will be used).


Testing SSL configuration
=========================
Now try the SSL configuration by pasting this URI into your web browser (exchange for your domain name):
https://www.ssllabs.com/ssltest/analyze.html?d=www.viltstigen.se
