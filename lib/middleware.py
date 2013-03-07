#!/usr/bin/env python
# -*- coding: utf-8 -*-

class StripPath(object):
    def __init__(self, wsgi):
        self.app = wsgi

    def __call__(self, environ, start_response):
        environ['PATH_INFO'] = environ['PATH_INFO'].rstrip('/')
        return self.app(environ, start_response)
