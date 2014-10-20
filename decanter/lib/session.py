#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .logger import Log
from .config import Config


class Session(object):

    def __init__(self, session=None):
        self.session = session

    def __getattr__(self, name):
        return getattr(self.session, name)

    def __getitem__(self, key):
        return self.session.get(key, None)

    def __setitem__(self, key, value):
        self.session.set(key, value)

    def __delitem__(self, key):
        self.session.delete(key)

    def __iter__(self):
        return self.session.__iter__()

    def __contains__(self, name):
        return self.session.__contains__(name)

    def __str__(self):
        return self.session.__str__()


class SessionAbstract(object):
    one_day = 60 * 60 * 24

    def __init__(self):
        # initialize logger
        self.log = Log.get_instance()
        # get config
        self.config = Config()

        # set session defaults
        self.name = 'DECANTERSESID'
        self.lifetime = 0
        if 'session' in self.config:
            # name of session cookie
            self.name = self.config.session.get('name', self.name)
            # session lifetime
            self.lifetime = self.config.session.get('lifetime', self.lifetime)

        # set cookie defaults
        self.path = '/'
        self.domain = None
        self.secure = False
        self.httponly = False
        if 'cookie' in self.config:
            # cookie path
            self.path = self.config.cookie.get('path', self.path)
            # cookie domain
            self.domain = self.config.cookie.get('domain', self.domain)
            # cookies secure over ssl only
            self.secure = self.config.cookie.get('secure', self.secure)
            # cookie over http only i.e. no javascript
            self.httponly = self.config.cookie.get('httponly', self.httponly)

        # the session data
        self.data = {}

    def write(self):
        raise NotImplementedError("write method not implemented")

    def read(self):
        raise NotImplementedError("read method not implemented")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def get_once(self, key, default=None):
        value = self.data.get(key, default)
        self.delete(key)
        return value

    def has(self, key):
        return key in self.data

    def set(self, key, value):
        self.data[key] = value

    def delete(self, key):
        try:
            del(self.data[key])
            return True
        except:
            return False

    def clear(self):
        self.data = {}

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
