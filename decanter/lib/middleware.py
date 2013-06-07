#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import uuid
import time
import urllib
import phpserialize
from bottle import request
from bottle import response
from lib.logger import Log
from lib.singleton import Singleton
from lib.crypt import Crypt
from lib.config import Config
from lib.store import Redis


class Session(Singleton):
    """ Middleware class to handle Session
    """
    one_day = 60*60*24

    def __init__(self, app):
        if getattr(self, '__init', False):
            # app must be a valid wsgi callable
            assert hasattr(app, '__call__'), 'app must be a valid wsgi callable'
            # the wsgi app
            self.app = app
            # initialize logger
            self.log = Log.get_instance()
            # get config
            config = Config.get_instance();
            # initialize crypt library
            self.crypt = Crypt(config.key)
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
            # the encrypted cookie value
            self.cookie = {'session_id': None,
                           'ip_address': None,
                           'user_agent': None,
                           'last_activity': None}


    def read(self):
        print(self.cookie)
        cookie = request.get_cookie(self.name)
        try:
            if cookie:
                cookie = urllib.unquote(cookie)
                cookie = self.crypt.decrypt(cookie)
                self.cookie = phpserialize.loads(cookie)
                if 'session_id' in self.cookie:
                    data = self.redis.get(self.skey)
                    if data:
                        self.data = phpserialize.loads(data, object_hook=phpserialize.phpobject)
                        print("data: {0}".format(self.data))
        except Exception as e:
            print("Error while reading session: {0}".format(e))
            self.log.error("Error while reading session: {0}".format(e))

        """
        try:
            if value:
                value = urllib.unquote(value)
                value = self.crypt.decrypt(value)
                data = phpserialize.loads(value)
                if 'session_id' in data:
                    self.skey = data['session_id']
            if self.skey:
                print("skey: {0}".format(self.skey))
                data = self.redis.get(self.skey)
                if data:
                    self.data = phpserialize.loads(data, object_hook=phpserialize.phpobject)
                    print("data: {0}".format(self.data))
        except Exception as e:
            self.log.error("Error while reading session: {0}".format(e))
        """


    def write(self):
        if len(self.data):
            pass

        if self.redis_key:
            max_age = self.lifetime if self.lifetime else None
            expires = (time.strftime('%a, %d-%b-%Y %T GMT',
                                     time.gmtime(time.time() + self.lifetime))) if self.lifetime else None
            params = {}
            if max_age:
                params['max_age'] = max_age
            if expires:
                params['expires'] = expires
            params['domain'] = self.domain
            params['path'] = self.path
            params['secure'] = self.secure
            params['httponly'] = self.httponly

            response.set_cookie(self.name, self.crypt.encrypt(self.skey), **params)


    def wsgi(self, environ, start_response):
        res = self.app(environ, start_response)
        self.read();
        return res

    def __call__(self, environ, start_response):
        res = self.wsgi(environ, start_response)
        return res

    def get_redis_key(self):
        if self.redis_key:
            return self.redis_key
        value = request.get_cookie(self.name)
        try:
            if value:
                value = urllib.unquote(value)
                value = self.crypt.decrypt(value)
                data = phpserialize.loads(value)
                if 'session_id' in data:
                    self.redis_key = data['session_id']

                if not self.redis_key:
                    data = {'session_id': self.md5(uuid.uuid4()),
                            'ip_address': request.remote_addr,
                            'user_agent': request.environment.get('HTTP_USER_AGENT')[0:50],
                            'last_activity': int(time.time())
                            }
                    data = phpserialize.dumps(data)


        except Exception as e:
            self.log.error("Error while reading session: {0}".format(e))

    def __getitem__(self, key):
        return self.data.get(key, None)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        try:
            del(self.data[key])
        except:
            pass

    def __iter__(self):
        return self.data.__iter__()

    def __contains__(self, name):
        return name in self.data

    def __str__(self):
        return self.data.__str__()


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
