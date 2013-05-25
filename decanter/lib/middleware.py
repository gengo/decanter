#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from bottle import request
from bottle import response
from lib.singleton import Singleton
from lib.config import Config
from lib.store import Redis

class Session(Singleton):
    def __init__(self, app):
        if getattr(self, '__init', False):
            # app must be a valid wsgi callable
            assert hasattr(app, '__call__'), 'app must be a valid wsgi callable'
            # the wsgi app
            self.app = app
            # get config
            config = Config.get_instance();
            # redis session storage
            self.redis = Redis();
            # name of session cookie
            self.name = config.session.get('name', 'DECANTERSESID')
            # session lifetime
            self.lifetime = config.session.get('lifetime', 0)
            # cookie path
            self.path = config.cookie.get('path', '/')
            # cookie domain
            self.domain = config.cookie.get('domain', None)
            # cookies secure over ssl only
            self.secure = config.cookie.get('secure', False)
            # cookie over http only i.e. no javascript
            self.httponly = config.cookie.get('httponly', False)
            # the session data
            self.data = {}
            # redis hash key
            self.hkey = None


    def read(self):
        self.hkey = request.get_cookie(self.name)


    def write(self):


    def wsgi(self, environ, start_response):
        res = self.app(environ, start_response)
        return res

    def __call__(self, environ, start_response):
        res = self.wsgi(environ, start_response)
        return res


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
            paths = self.config.apppath.strip(os.path.sep).split(os.path.sep)
            app = paths.pop()
            name = '.'.join(
                [app, 'bundles', self.bundle, 'controllers', self.controller])
            if name not in sys.modules:
                appdir = os.sep.join(path for path in paths)
                if appdir not in sys.path:
                    sys.path.insert(0, appdir)
                __import__(name, fromlist=[self.controller])

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
