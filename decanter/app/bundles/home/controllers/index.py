#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.decorator import get
from lib.store import Redis


@get('/', apply='json', skip='jinja2')
def index():
    redis = Redis()
    redis.set('name', 'andrea')
    redis.expire('name', 20)
    return {'word': 'Hello Decanter!'}


@get('/home/')
@get('/home/<name>')
def home(name='Decanter'):
    return {'greeting': "Hello {0}!".format(name.lower().capitalize())}
