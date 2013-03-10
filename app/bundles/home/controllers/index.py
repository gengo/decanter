#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import route

@route('/')
def index():
    return 'Hello Decanter!'