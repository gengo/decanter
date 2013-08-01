#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import request
from lib.decorator import get


@get('/', apply='json', skip='jinja2')
def index():
    ses = request.environ.get('express.session', {})
    print ses
    ses['name'] = 'World!'
    if ses.has('name'):
        return {'word': ses['name']}
    return {'word': 'Hello Decanter!'}


@get('/home/')
@get('/home/<name>')
def home(name='Decanter'):
    return {'greeting': "Hello {0}!".format(name.title())}
