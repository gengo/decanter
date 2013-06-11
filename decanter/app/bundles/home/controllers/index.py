#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.decorator import get
from lib.session import Session


@get('/', apply='json', skip='jinja2')
def index():
    ses = Session.get_instance()
    print ses
    ses['name'] = 'Decanter!'
    if ses.has('decanter'):
        return {'word': ses['decanter']}
    return {'word': 'Hello Decanter!'}


@get('/home/')
@get('/home/<name>')
def home(name='Decanter'):
    return {'greeting': "Hello {0}!".format(name.title())}
