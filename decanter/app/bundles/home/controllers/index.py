#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.decorator import route
from lib.decorator import get
from app.common import errors


@get('/', apply='json', skip='jinja2')
def index():
    return {'word': 'Hello Decanter!'}


@get('/home/')
@get('/home/<name>')
def home(name='Decanter'):
    return {'greeting': "Hello {0}!".format(name.lower().capitalize())}
