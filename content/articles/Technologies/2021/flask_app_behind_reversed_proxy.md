Title: Flask application behind a reverse proxy
Author: Mats Melander
Date: 2021-09-13
Modified: 2021-09-14
Tags: Python, flask, nginx, gunicorn, wsgi 
Category: Technologies
Summary: A description how to manage a flask application that is behind a reverse proxy

# Introduction
I have a Flask-application that is externally accessed via an nginx proxy. Using this configuration I encountered
a problem to access the full content, described below.

After some investigation, I found out that the fix for this problem was to set the value of a WSGI environment
variable named `SCRIPT_NAME`.

# Description
A web-client access the link [https://www.viltstigen.se/tv_ws?stn=Lund](https://www.viltstigen.se/tv_ws?stn=Lund).
The web-server at domain `viltstigen.se` is a nginx proxy, that passes the request to another node in my network that 
is running gunicorn/flask application stack. Flask generates html content that is passed back to the original web-client.

In the html-template that flask is using to generate html code, I have
```
<script src="{{ url_for('static', filename='ws.js') }}"></script>
```
which in turn will generate this
```html
<script src="static/ws.js"></script>
```
which causes the web-client to request `https://www.viltstigen.se/static/ws.js` which in turn causes a 404 return.

What we want instead is
```html
<script src="tv_ws/static/ws.js"></script>
```
that becomes `https://www.viltstigen.se/tv_ws/static/ws.js`.

So how to get `tv_ws` into the URL?

An extensive description is found [here](https://dlukes.github.io/flask-wsgi-url-prefix.html).
It boils down to setting the value of the WSGI environment variable `SCRIPT_NAME` to `tv_ws`.

If you set `SCRIPT_NAME=/tv_ws`, WSGI guarantees that the web server running the app will strip this prefix from 
incoming URLs, and add it to outgoing URLs.

Here is how I do it in my flask application

```python
class ReverseProxied(object):
    def __init__(self, app, script_name):
        self.app = app
        self.script_name = script_name

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = self.script_name
        return self.app(environ, start_response)


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app, script_name='/tv_ws')
```
Note that if `SCRIPT_NAME` already have a value (default value is "") it will be overwritten.
Here, the `wsgi_app` object of the flask app is extended with the ReverseProxied-class. According to the 
[WSGI specification](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface), the application should call
start_response (which is a server callback function), this is done within flask. The extended flask application sets
the value of `SCRIPT_NAME` and call the original flask application object.

Several other solutions are discussing of setting the configuration of nginx instead, as an example see
[https://stackoverflow.com/questions/25962224/running-a-flask-application-at-a-url-that-is-not-the-domain-root](https://stackoverflow.com/questions/25962224/running-a-flask-application-at-a-url-that-is-not-the-domain-root)