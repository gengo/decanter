#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


class Dispatcher(object):
    """
    dispatch a request to one of the bundles controllers
    """
    def __init__(self, wsgi, config):
        self.app = wsgi
        self.config = config
        self.bundle = None
        self.controller = None

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
        try:
            app = self.config.apppath.strip(os.path.sep).split(os.path.sep).pop()
            name = '.'.join([app, 'bundles', self.bundle, 'controllers', self.controller])
            if name not in sys.modules:
                __import__(name, fromlist=[self.controller])

        except Exception as e:
            print("Dispatcher: {0}".format(e))


    def is_bundle(self, bundle):
        path = os.path.join(self.config.apppath, 'bundles', bundle)
        return os.path.isdir(path)

    def is_controller(self, bundle, controller):
        path = os.path.join(self.config.apppath, 'bundles', bundle, 'controllers', '.'.join([controller, 'py']))
        return os.path.isfile(path)


    def __call__(self, environ, start_response):
        self.route(environ['PATH_INFO'])
        self.dispatch()
        return self.app(environ, start_response)


class StripPath(object):
    def __init__(self, wsgi):
        self.app = wsgi

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'] != '/':
            environ['PATH_INFO'] = environ['PATH_INFO'].rstrip('/')
        return self.app(environ, start_response)
