#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.decorator import get
from lib.store import Redis
from lib.middleware import Session


@get('/', apply='json', skip='jinja2')
def index():
    ses = Session.get_instance()
    ses['name'] = 'andrea'
    return {'word': 'Hello Decanter!'}


@get('/home/')
@get('/home/<name>')
def home(name='Decanter'):
    return {'greeting': "Hello {0}!".format(name.lower().capitalize())}
