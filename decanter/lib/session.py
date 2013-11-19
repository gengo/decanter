#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import uuid
import urllib
import calendar
import phpserialize
from bottle import request
from bottle import response
from .logger import Log
from .crypt import Crypt
from .store import Redis
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


class ExpressSession(SessionAbstract):

    def __init__(self, cookies):
        super(ExpressSession, self).__init__()
        # SimpleCookie object
        self.cookies = cookies
        # initialize crypt library
        self.crypt = Crypt(self.config.key)
        # redis session storage
        self.redis = Redis()
        # the encrypted cookie value
        self.cookie = {'session_id': None,
                       'ip_address': None,
                       'user_agent': None,
                       'last_activity': None}

    def read(self):
        cookie = False
        if self.name in self.cookies:
            cookie = self.cookies[self.name].value
        try:
            if cookie:
                cookie = urllib.unquote(cookie)
                cookie = self.crypt.decrypt(cookie)
                self.cookie = phpserialize.loads(cookie)
                if 'session_id' in self.cookie:
                    data = self.redis.get(self.cookie['session_id'])
                    if data:
                        self.data = phpserialize.loads(
                            data, object_hook=phpserialize.phpobject)
                    else:
                        self.data = {}
                        for key in self.cookie:
                            self.cookie[key] = None

        except Exception as e:
            print("Error while reading session: {0}".format(e))
            self.log.error("Error while reading session: {0}".format(e))

    def write(self):
        if self.cookie['session_id']:
            self.save()
        else:
            self.create()

    def save(self):
        timestamp = calendar.timegm(time.gmtime())
        max_age = self.lifetime if self.lifetime else self.one_day
        expires = timestamp + max_age

        params = {}
        if max_age:
            params['max_age'] = max_age
        if expires:
            params['expires'] = expires
        params['domain'] = self.domain
        params['path'] = self.path
        if self.secure:
            params['secure'] = self.secure
        if self.httponly:
            params['httponly'] = self.httponly

        data = phpserialize.dumps(
            self.data, object_hook=phpserialize.phpobject)
        self.redis.set(self.cookie['session_id'], data)
        response.set_cookie(self.name, urllib.quote_plus(
            self.crypt.encrypt(phpserialize.dumps(self.cookie))), **params)

    def create(self):
        timestamp = calendar.timegm(time.gmtime())

        self.cookie['session_id'] = self.crypt.md5(uuid.uuid4().get_bytes())
        self.cookie['ip_address'] = request.remote_addr
        self.cookie['user_agent'] = request.environ.get('HTTP_USER_AGENT', '')[0:50]
        self.cookie['last_activity'] = timestamp

        max_age = self.lifetime if self.lifetime else self.one_day
        expires = timestamp + max_age

        params = {}
        if max_age:
            params['max_age'] = max_age
        if expires:
            params['expires'] = expires
        params['domain'] = self.domain
        params['path'] = self.path
        if self.secure:
            params['secure'] = self.secure
        if self.httponly:
            params['httponly'] = self.httponly

        data = phpserialize.dumps(
            self.data, object_hook=phpserialize.phpobject)
        self.redis.set(self.cookie['session_id'], data)
        self.redis.expire(self.cookie['session_id'], max_age)
        response.set_cookie(self.name, urllib.quote_plus(
            self.crypt.encrypt(phpserialize.dumps(self.cookie))), **params)

    def __str__(self):
        return ':'.join([self.cookie['session_id'] if self.cookie['session_id'] else '', self.data.__str__()])
