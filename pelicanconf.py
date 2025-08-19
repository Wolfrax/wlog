#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Mats Melander'
SITENAME = 'Wolfblog'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Viltstigen', 'https://www.viltstigen.se/'),
         ('Wolfblog', 'http://wlog.viltstigen.se/'),
         ('Github', 'https://github.com/wolfrax'),)

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# bootstrap3 theme settings, see https://github.com/getpelican/pelican-themes/tree/master/pelican-bootstrap3
THEME = "/home/mm/dev/wlog/pelican-themes/pelican-bootstrap3" 
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

ARTICLE_PATHS = ['articles']
STATIC_PATHS = ['img', 'pdf', 'extra', 'extra/robots.txt', 'extra/favicon.ico', 'components']
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

# Plugins are installed (git clone) into the virtual environment for wlog
PLUGIN_PATHS = ['/home/mm/dev/wlog/venv/lib/python3.10/site-packages/pelican/pelican-plugins']

# liquid_tags.notebook: For including Jupyter notebooks {% notebook example.ipynb % }
#         See https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags#ipython-notebooks
# i18n_subsites: For translations, needed for bootstrap3 theme
#         See https://github.com/getpelican/pelican-themes/tree/master/pelican-bootstrap3#installation
PLUGINS = ['liquid_tags.notebook', 'i18n_subsites']

IGNORE_FILES = ['.ipynb_checkpoints']
NOTEBOOK_DIR = 'notebooks'  # Next to articles in the content directory, store Jupyter notebooks here
MARKUP = ("md", "ipynb")

# Include the _nb_header.html styling file, generated automatically by liquid_tags.notebook at first run
from io import open
EXTRA_HEADER = open('_nb_header.html', encoding='utf-8').read()