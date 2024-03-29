Title: Pelican bootstrap3 theme and Jupyter
Author: Mats Melander
Date: 2020-06-18
Modified: 2022-11-20
Tags: Pelican
Category: Technologies
Summary: A note on using Pelican bootstrap3 theme

I decided to switch from Pelican [elegant theme](https://github.com/Pelican-Elegant/elegant>) to 
the [bootstrap3 theme](https://github.com/getpelican/pelican-themes/tree/master/pelican-bootstrap3).

The main reason was to be able to include [Jupyter notebooks](https://jupyter.org/) in the blog articles.
How to do this was documented for bootstrap3 but not for elegant themes, meaning that it might be possible for the latter 
theme also.

A few adaptions were needed to make this work.

> Note, as of 2021-04-30, nbconvert version 5.x needs to be installed. If version 6.x
> is used, there will be an error that the template basic cannot be found when generating pelican content
> See [this note](https://github.com/danielfrg/pelican-jupyter/issues/126)

First install themes, for example (using virtualenvironment venv) and plugins.
Below will install **all** themes and plugins.

```bash
git clone --recursive https://github.com/getpelican/pelican-themes /home/mm/dev/wlog/venv/lib/python3.8/site-packages/pelican/themes
git clone --recursive https://github.com/getpelican/pelican-plugins /home/mm/dev/wlog/venv/lib/python3.8/site-packages/pelican/pelican-plugins
```
I use the [liquid_tags](https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags#ipython-notebooks) 
plugin to include Jupyter notebooks in blog articles without losing the styling of these notebooks. See below and 
liquid_tags documentation.

Add this to `pelicanconf.py`, which enables 2 plugins
```python
# Plugins are installed (git clone) into the conda virtual environment for wlog
PLUGIN_PATHS = ['/home/mm/dev/wlog/venv/lib/python3.8/site-packages/pelican/pelican-plugins']

# liquid_tags.notebook: For including Jupyter notebooks {% notebook example.ipynb % }
#         See https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags#ipython-notebooks
# i18n_subsites: For translations, needed for bootstrap3 theme
#         See https://github.com/getpelican/pelican-themes/tree/master/pelican-bootstrap3#installation
PLUGINS = ['liquid_tags.notebook', 'i18n_subsites']

IGNORE_FILES = ['.ipynb_checkpoints']
NOTEBOOK_DIR = 'notebooks'  # Next to articles in the content directory, store Jupyter notebooks here

# Include the _nb_header.html styling file, generated automatically by liquid_tags.notebook at first run
from io import open
EXTRA_HEADER = open('_nb_header.html', encoding='utf-8').read()
``` 
Using this syntax in a markdown file will include the file `example.ipynb` from the notebooks directory (sub directory 
to content).
```
{% notebook example.ipynb %}
```
Now add below at the top in the file `base.html` for the bootstrap theme, this will include `_nb_header.html`
that is generated first time pelican generates content. `nb_header.html` includes all Jupyter notebook
styling elements (Twitter bootstrap).
(File located at `/home/mm/dev/wlog/venv/lib/python3.8/site-packages/pelican/themes`)
```jinja2
{% if EXTRA_HEADER %}
{{ EXTRA_HEADER }}
{% endif %}
```
Using the latest version of `liquid_tags.notebook` I encountered a problem probably due to a configuration issue in my setup.
```
ERROR: Could not process articles/Technologies/exmaple.md
  | NameError: name 'settings' is not defined
```
In the file `notebook.py` I made the following update which fixed the problem for me (commented row is original code).
(/home/mm/dev/wlog/venv/lib/python3.8/site-packages/pelican/pelican-plugins/liquid_tags/notebook.py)
```python
    # nb_path = os.path.join(settings.get('PATH', 'content'), nb_dir, src)
    nb_path = os.path.join('content', nb_dir, src)
```

To configure the bootstrap3 theme these settings were added in `pelicanconf.py`.
```python
# bootstrap3 theme settings, see https://github.com/getpelican/pelican-themes/tree/master/pelican-bootstrap3
THEME = "pelican-bootstrap3"
JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}
PYGMENTS_STYLE = 'default'  # See https://help.farbox.com/pygments.html for examples
SITELOGO = 'img/Wolf_logo.png'
SITELOGO_SIZE = 30
DISPLAY_ARTICLE_INFO_ON_INDEX = True
DISPLAY_RECENT_POSTS_ON_SIDEBAR = True
GITHUB_USER = "wolfrax"
DISPLAY_PAGES_ON_MENU = True
MENUITEMS = [('Archive', '/archives.html')]
YEAR_ARCHIVE_SAVE_AS = 'archive/{date:%Y}/index.html'
MONTH_ARCHIVE_SAVE_AS = 'archive/{date:%Y}/{date:%b}/index.html'
DISPLAY_ARCHIVE_ON_SIDEBAR = True
```

To enable [applause button](https://applause-button.com/) into bootstrap3 theme for articles, some simple tweaks are needed.
In the bootstrap3 file `article.html`, add the last 2 lines below.
(Located at /home/mm/dev/wlog/venv/lib/python3.8/site-packages/pelican/themes/pelican-bootstrap3/templates)
```jinja2
{% block meta %}
    {% if article.author %}
        <meta name="author" content="{{ article.author }}" />
    {% else %}
        <meta name="author" content="{{ AUTHOR }}" />
    {% endif %}
    {% if article.tags %}
        <meta name="keywords" content="{{ article.tags|join(',')|striptags }}" />
    {% endif %}
    {% if article.summary %}
        <meta name="description" content="{{ article.summary|striptags|escape }}" />
    {% endif %}
     <!-- MM: add the button style & script -->
    <link rel="stylesheet" href="https://unpkg.com/applause-button/dist/applause-button.css" />
    <script src="https://unpkg.com/applause-button/dist/applause-button.js"></script>
{% endblock %}
```
Then, to show it at the end of the article, add the `<applause-button>`-tag in `article.html`
```jinja2
            {% include 'includes/show_source.html' %}
            <!-- MM: add the button! -->
            <applause-button style="width: 58px; height: 58px;"/>
        </article>
```

**Update 2022-11-20** To enable Google Analytics 4, the file `ga.html` 
(located at /home/mm/dev/wlog/venv/lib/python3.8/site-packages/pelican/themes/pelican-bootstrap3/templates/includes) is
updated. The content of this file as per below.
```jinja2
{% if GOOGLE_ANALYTICS %}

<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={{GOOGLE_ANALYTICS}}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', '{{GOOGLE_ANALYTICS}}');
</script>

{% endif %}
{% if GOOGLE_ANALYTICS_UNIVERSAL %}
    <!-- Google Analytics Universal -->
    <script type="text/javascript">
        (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
        (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
        m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
        })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

        ga('create', '{{ GOOGLE_ANALYTICS_UNIVERSAL }}', '{{ GOOGLE_ANALYTICS_UNIVERSAL_PROPERTY }}');
        ga('send', 'pageview');
    </script>
    <!-- End Google Analytics Universal Code -->
{% endif %}
```
Note that the last part, under GOOGLE_ANALTYICS_UNIVERSAL, is not used by me, but I left it there.
In `publishconf.py`, add this
```python
GOOGLE_ANALYTICS  = "Whatever-your-identifier-is"
```