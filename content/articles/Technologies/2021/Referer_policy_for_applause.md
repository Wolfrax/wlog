Title: Setting referer policy when using applause button
Author: Mats Melander
Date: 2021-07-14
Modified: 2021-07-16
Tags: Blog, Applause, nginx, chrome
Category: Technologies
Summary: Description on how, and why, to set referer policy when using applause button

When blogging I use [applause button](<https://applause-button.com/>) to allow claps and keep track of the number of
claps I got (not many). How to use this with Pelican and the bootstrap3 theme is described 
[here](https://wlog.viltstigen.se/articles/2020/06/18/pelican-bootstrap3-theme-and-jupyter/) and
[here](https://wlog.viltstigen.se/articles/2020/02/12/pelican-applause-button/).

In the second link, I describe how to query the number of claps and make a summary list.

Over time, I noticed a deviation from the number of claps stated in the summary list and what was shown in the
blog entries. Investigating this, I noted that a claps where counted on the URI (in my case 'wlog.vilstigen.se') and not
on individual blog entries (like "https://wlog.viltstigen.se/articles/2020/02/12/pelican-applause-button/"). 

How come?

Previously, it looked like a clap was registered on the blog entry and not for the URI.

Checking the documentation for applause button I noted:

> The applause button determines the URL that it should log a 'clap' for based on the HTTP referrer.

So, to register the clap on the full blog entry path, the "Referer" [sic] in the request header has to be set to the
right value. Checking the referrer value with Chrome browser developer tools, this was not the case. It was set to 
the URI.

In my configuration, I use nginx as a reverse-proxy. The reverse-proxy receives the browser request for a blog entry, 
then it sends the request further upstream to another nginx server that acts as a web-server for pelican generated 
blog content. The web-server responds and send the response downstream to the nginx reverse-proxy which in turn send 
the response back to the browser. This is a common configuration using nginx.

After thinking on this, I suspected that my nginx configuration was not setup correctly. After some more checking, I
found this applause-button reported [issue](https://github.com/ColinEberhardt/applause-button/issues/72), which
pointed in the right direction. A good link that describe the default behavior by chrome is
[here](https://developers.google.com/web/updates/2020/07/referrer-policy-new-chrome-default).

(I have only tried this with chrome browser, so I don't know if it is applicable for other browsers.)

In the same issue, it is suggested to set the referrer policy to "no-referrer-when-downgrade".
Checking the [specification](https://www.w3.org/TR/referrer-policy/) for this policy indicated that setting the
referer policy in the reverse-proxy is a good idea.

From [Mozilla](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy) this is stated for 
no-referrer-when-downgrade:

> Send the origin, path, and querystring in Referer when the protocol security level stays the same or improves 
> (HTTP→HTTP, HTTP→HTTPS, HTTPS→HTTPS). Don't send the Referer header for requests to less secure destinations 
> (HTTPS→HTTP, HTTPS→file).


For nginx (in the reverse proxy) this is done like so (see the "add_header" directive below)

```bash
server {
    # Reverse proxy to rpi2.local 

    listen 443 ssl;
    listen [::]:443 ssl;

    server_name wlog.viltstigen.se;

    # SSL configuration
    include snippets/ssl-wlog.viltstigen.se.conf;
    include snippets/ssl-params.conf;

    location / {
        add_header Referrer-Policy "no-referrer-when-downgrade"; # See https://github.com/ColinEberhardt/applause-button/issues/72
        proxy_pass http://192.168.1.51; # rpi2.local
    }

    location /.well-known/ {}  # do not redirect for this directory, used by letsencrypt
}
```

Applying this change to the reverse-proxy (in my case installed on node rpi1.local, the pelican web-server is on 
rpi2.local) worked for me. I could now see that the referer header was set to the full path, and thus the clap is 
registered on the right place. The add_header directive, means that the value of this field is set in the response to
the browser. The browser will then include the full path to the blog entry when using the applause button API, rather
than using only the URI value.

On the semantics of "no-referrer-when-downgrade" value, please check the 
[specification](https://www.w3.org/TR/referrer-policy/).


