#!/usr/bin/env python
# -*- coding: utf-8 -*-

debug = True

user = 'www-data'
group = 'www-data'

pidfile = "/var/run/decanter_{0}.py"

hostname = 'localhost'
port = 9001

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
