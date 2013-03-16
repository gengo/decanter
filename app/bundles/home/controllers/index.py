#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.decorator import route
from lib.decorator import get


@get('/')
def index():
    return {'word': 'Hello Decanter!'}