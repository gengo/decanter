#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Dispatcher(object):
    def __init__(self, wsgi):
        self.app = wsgi

    def wsgi(self, environ, start_response):
        print(environ['PATH_INFO'])
        return self.app

    def __call__(self, environ, start_response):
        res = self.wsgi(environ, start_response)
        return res(environ, start_response)
