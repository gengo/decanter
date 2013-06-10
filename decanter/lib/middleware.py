#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from logger import Log
from config import Config
from errors import ValidationError


class Dispatcher(object):
    """
    dispatch a request to one of the bundles controllers
    """

    def __init__(self, wsgi, config):
        self.app = wsgi
        self.config = config
        self.bundle = None
        self.controller = None
        if config.debug:
            self.imported = {}

    def route(self, path):
        segs = []
        if path != '/':
            segs = path.strip('/').split('/')
        if not len(segs):
            self.bundle = self.config.default['bundle']
            self.controller = self.config.default['controller']
        else:
            if self.is_bundle(segs[0]):
                self.bundle = segs[0]
                segs.pop(0)
                if not len(segs):
                    self.controller = self.config.default['controller']
                else:
                    if self.is_controller(self.bundle, segs[0]):
                        self.controller = segs[0]
                        segs.pop(0)
                    else:
                        self.controller = self.config.default['controller']
            elif self.is_bundle(self.config.default['bundle']):
                self.bundle = self.config.default['bundle']
                if self.is_controller(self.bundle, segs[0]):
                    self.controller = segs[0]
                    segs.pop(0)
                else:
                    self.controller = self.config.default['controller']

    def dispatch(self):
        def to_imported_key(name):
            return self.controller + '-' + name
        try:
            paths = self.config.apppath.strip(os.path.sep).split(os.path.sep)
            app = paths.pop()
            name = '.'.join(
                [app, 'bundles', self.bundle, 'controllers', self.controller])
            if name not in sys.modules:
                appdir = os.sep.join(path for path in paths)
                if appdir not in sys.path:
                    sys.path.insert(0, appdir)
                module = __import__(name, fromlist=[self.controller])
                if self.config.debug:
                    self.imported[to_imported_key(name)] = module
            elif self.config.debug:
                reload(self.imported[to_imported_key(name)])

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print("Dispatcher: {0}".format(e))
            print(tb)

    def is_bundle(self, bundle):
        path = os.path.join(self.config.apppath, 'bundles', bundle)
        return os.path.isdir(path)

    def is_controller(self, bundle, controller):
        path = os.path.join(self.config.apppath, 'bundles',
                            bundle, 'controllers',
                            '.'.join([controller, 'py']))
        return os.path.isfile(path)

    def wsgi(self, environ, start_response):
        self.route(environ['PATH_INFO'])
        self.dispatch()
        return self.app

    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)(environ, start_response)


class StripPath(object):

    def __init__(self, wsgi):
        self.app = wsgi

    def wsgi(self, environ, start_response):
        if environ['PATH_INFO'] != '/':
            environ['PATH_INFO'] = environ['PATH_INFO'].rstrip('/')
        return self.app

    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)(environ, start_response)
