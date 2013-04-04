#!/usr/bin/env python
# -*- coding: utf-8 -*-

debug = True

user = 'www-data'
group = 'www-data'

# pid file
pidfile = "/var/run/decanter_{0}.py"

# logging
logger = {
    # log directory path, first {0} is the port number and second {1] is the date
    'filepath': '/var/log/decanter_{0}-{1}.log',
    # DEBUG, INFO, WARNING, ERROR, FATAL
    'level': 'DEBUG'
}

import os
import sys
# the application directory
apppath = os.path.join(os.path.realpath(os.path.dirname(os.path.dirname(__file__))), 'app')

# default routes
default = {
    'bundle': 'home',
    'controller': 'index'
}

# list of plugins names to install by default
plugins = ['jinja2']
