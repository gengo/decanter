#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.decorator import get


@get('/', apply='json', skip='jinja2')
def index():
    return {'word': 'Hello Decanter!'}


@get('/home/')
@get('/home/<name>', timeout=30)
def home(name='Decanter'):
    return {'greeting': "Hello {0}!".format(name.title())}
